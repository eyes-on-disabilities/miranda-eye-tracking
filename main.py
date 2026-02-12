import argparse
import queue
import time
import traceback
from datetime import datetime, timedelta
from threading import Event, Thread
from typing import Callable, Iterator, List, Optional, Tuple

import numpy as np
import screeninfo

import calibration
import config
from calibration import CalibrationInstruction, CalibrationResult
from input_methods import input_methods
from guis.tkinter.calibration_window import CalibrationWindow, CalibrationWindowButton
from guis.tkinter.main_menu_window import MainMenuWindow
from guis.tkinter.release_notes_window import show_release_notes_if_needed
from misc import Vector
from mouse_movement import MouseMovementType
from output_methods import output_methods
from tracking_approaches import tracking_approaches

import logging
import sys

if getattr(sys, "frozen", False):
    import pyi_splash
    pyi_splash.close()

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input-method",
    help='The method to get eye- or head-tracking data from. default="%(default)s"',
    choices=input_methods,
    default=next(iter(input_methods)),  # the first mentioned key
)
parser.add_argument(
    "--tracking-approach",
    type=str,
    help='The tracking approach to transform the user\'s gaze into a certain mouse movement. default="%(default)s"',
    choices=tracking_approaches,
    default=next(iter(tracking_approaches)),
)
parser.add_argument(
    "--output-method",
    help='The method for how to use the eye- or head-tracking data. default="%(default)s"',
    choices=output_methods,
    default=next(iter(output_methods)),
)
parser.add_argument(
    "--log-level",
    help='default="%(default)s"',
    default="INFO",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
)

args = parser.parse_args()


def setup_logging(args) -> None:
    level = getattr(logging, args.log_level)

    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root.handlers.clear()
    root.addHandler(handler)


setup_logging(args)

selected_input_method = None
selected_tracking_approach = None
selected_output_method = None

input_method = None
tracking_approach = None
output_method = None

stop_event = Event()

calibration_result = None
temp_calibration_result = None

main_menu_window = None
calibration_window = None
in_calibration = False

request_loop_thread = None
last_input_method_vector = None
monitor = screeninfo.get_monitors()[0]
last_mouse_position = [monitor.width / 2, monitor.height / 2]

logger = logging.getLogger(__name__)

logger.info(f"{config.APP_FULL_NAME} {config.APP_VERSION}")

UiMsg = Tuple[str, object]
ui_queue: "queue.SimpleQueue[UiMsg]" = queue.SimpleQueue()


def reload_input_method(input_method_key, root_window):
    logger.info(f"reload input method: {input_method_key}")
    global selected_input_method, input_method
    selected_input_method = input_method_key
    if input_method is not None:
        input_method.stop()
    input_method = input_methods[selected_input_method].clazz(root_window)
    input_method.start()


def reload_tracking_approach(tracking_approach_key):
    logger.info(f"reload tracking approach: {tracking_approach_key}")
    global selected_tracking_approach, tracking_approach
    selected_tracking_approach = tracking_approach_key
    tracking_approach = tracking_approaches[selected_tracking_approach].clazz()


def reload_output_method(output_method_key, root_window):
    logger.info(f"reload output method: {output_method_key}")
    global selected_output_method, output_method
    selected_output_method = output_method_key
    if output_method is not None:
        output_method.stop()
    output_method = output_methods[selected_output_method].clazz(root_window)
    output_method.start()


def reload_calibration_result():
    logger.info("reload calibration result")
    global selected_input_method, selected_tracking_approach, tracking_approach
    global calibration_result, main_menu_window, last_mouse_position
    calibration_result = None
    last_mouse_position = [monitor.width / 2, monitor.height / 2]
    if calibration.has_result(selected_input_method, selected_tracking_approach):
        calibration_result = calibration.load_result(selected_input_method, selected_tracking_approach)
        tracking_approach.calibrate(calibration_result)
    main_menu_window.set_has_calibration_result(calibration_result is not None)


def loop():
    global last_input_method_vector, last_mouse_position
    while not stop_event.is_set():
        try:
            last_input_method_vector = input_method.get_next_vector()

            ui_queue.put(("input_method_has_data", last_input_method_vector is not None))

            if last_input_method_vector is not None and tracking_approach.is_calibrated():
                mouse_movement = tracking_approach.get_next_mouse_movement(last_input_method_vector)
                if mouse_movement is not None:
                    last_mouse_position = get_new_mouse_position(mouse_movement, last_mouse_position)

                    # Schedule UI update (Tk thread will decide which window to paint on)
                    ui_queue.put(("mouse_point", tuple(last_mouse_position)))

                    # Publisher might touch Tk internally; keep on Tk thread too
                    ui_queue.put(("output_method_push", tuple(last_mouse_position)))

            else:
                ui_queue.put(("unset_mouse_point", None))

        except Exception:
            traceback.print_exc()

        time.sleep(config.LOOP_SLEEP_IN_MILLISEC / 1000)


def poll_ui():
    # Runs on Tk thread only
    if stop_event.is_set():
        return

    while True:
        try:
            msg, payload = ui_queue.get_nowait()
        except Exception:
            break

        try:
            if msg == "input_method_has_data":
                if main_menu_window is not None:
                    main_menu_window.set_input_method_has_data(bool(payload))

            elif msg == "unset_mouse_point":
                if calibration_window is None:
                    if main_menu_window is not None:
                        main_menu_window.unset_mouse_point()
                else:
                    if calibration_window is not None and not in_calibration:
                        calibration_window.unset_mouse_point()

            elif msg == "mouse_point":
                pos = payload
                if pos is None:
                    continue

                if calibration_window is not None:
                    if not in_calibration:
                        calibration_window.set_mouse_point(pos)
                else:
                    if main_menu_window is not None:
                        main_menu_window.unset_mouse_point()
                        main_menu_window.set_mouse_point(pos)

            elif msg == "output_method_push":
                pos = payload
                if output_method is not None and pos is not None:
                    output_method.push(pos)

        except Exception:
            traceback.print_exc()

    try:
        root_window.after(15, poll_ui)
    except Exception:
        pass


def on_close():
    if stop_event.is_set():
        return
    stop_event.set()

    try:
        if input_method is not None:
            input_method.stop()
    except Exception:
        traceback.print_exc()

    try:
        if output_method is not None:
            output_method.stop()
    except Exception:
        traceback.print_exc()

    try:
        if calibration_window is not None:
            calibration_window.close_window()
    except Exception:
        pass

    try:
        root_window.destroy()
    except Exception:
        pass


def close_and_unset_calibration_window():
    global calibration_window, in_calibration
    in_calibration = False
    if calibration_window is not None:
        calibration_window.close_window()
    calibration_window = None


def accept_or_reject_temp_calibration_result(accept_temp_calibration_result: bool):
    global temp_calibration_result, calibration_result
    if accept_temp_calibration_result:
        calibration_result = temp_calibration_result
        calibration.delete_result(selected_input_method, selected_tracking_approach)
        calibration.save_result(selected_input_method, selected_tracking_approach, calibration_result)
    else:
        tracking_approach.calibrate(calibration_result)
    temp_calibration_result = None
    main_menu_window.set_has_calibration_result(calibration_result is not None)


def redo_calibration():
    if not in_calibration and calibration_window is not None:
        calibration_window.unset_buttons()
        on_calibration_requested(calibration_window)


def show_final_text_for_seconds(seconds, on_finish):
    if in_calibration or calibration_window is None:
        return
    if seconds == 0:
        on_finish()
    else:
        calibration_window.set_main_text(
            "Calibration Done. Do you like this calibration?"
            + "\nEither click or look at the options below."
            + f"\nIf you don't decide, a re-calibration starts in {seconds}"
        )
        calibration_window.after(1000, show_final_text_for_seconds, seconds - 1, on_finish)


def calibration_done():
    global in_calibration
    in_calibration = False
    calibration_window.set_buttons(
        [
            CalibrationWindowButton(
                text="Keep Calibration\n(or press <Enter>)",
                func=lambda: (close_and_unset_calibration_window(), accept_or_reject_temp_calibration_result(True)),
                sequence="<Return>",
            ),
            CalibrationWindowButton(
                text='Redo Calibration\n(or press "r")',
                func=redo_calibration,
                sequence="r",
            ),
            CalibrationWindowButton(
                text="Cancel and Close\n(or press <Escape>)",
                func=lambda: (close_and_unset_calibration_window(), accept_or_reject_temp_calibration_result(False)),
                sequence="<Escape>",
            ),
        ]
    )
    show_final_text_for_seconds(config.SHOW_FINAL_CALIBRATION_TEXT_FOR_SEC, redo_calibration)


def on_calibration_requested(new_calibration_window: CalibrationWindow):
    global calibration_window, in_calibration
    calibration_window = new_calibration_window

    in_calibration = True
    calibration_window.unset_mouse_point()

    calibration_instructions = tracking_approach.get_calibration_instructions()
    show_preparational_text(
        calibration_instructions.preparational_text,
        lambda: execute_calibrations(iter(calibration_instructions.instructions), calibration_done),
    )


def show_preparational_text(preparational_text: str, on_finish: Callable, end_time=None):
    now = datetime.now()
    if end_time is None:
        end_time = now + timedelta(seconds=config.SHOW_PREP_CALIBRATION_TEXT_FOR_SEC)

    if end_time < now:
        if calibration_window is not None:
            calibration_window.unset_main_text()
        on_finish()
    else:
        remaining_seconds = int((end_time - now).total_seconds())
        if calibration_window is not None:
            calibration_window.set_main_text(
                preparational_text
                + "\nYou can close this window by pressing <Escape>."
                + f"\nInstructions come in {remaining_seconds}"
            )
            calibration_window.bind("<Escape>", lambda _: close_and_unset_calibration_window())
            calibration_window.after(250, show_preparational_text, preparational_text, on_finish, end_time)


def scale_vector_to_screen(vector):
    return ((vector[0] + 1) * 0.5 * monitor.width, (vector[1] - 1) * 0.5 * -monitor.height)


def get_new_mouse_position(mouse_movement, last_mouse_position):
    if mouse_movement.type == MouseMovementType.TO_POSITION:
        new_mouse_position = scale_vector_to_screen(mouse_movement.vector)
    if mouse_movement.type == MouseMovementType.BY:
        new_mouse_position = [
            last_mouse_position[0] + mouse_movement.vector[0] * config.MOUSE_SPEED_IN_PX,
            last_mouse_position[1] - mouse_movement.vector[1] * config.MOUSE_SPEED_IN_PX,
        ]
        if new_mouse_position[0] < 0:
            new_mouse_position[0] = 0
        if new_mouse_position[0] > monitor.width:
            new_mouse_position[0] = monitor.width
        if new_mouse_position[1] < 0:
            new_mouse_position[1] = 0
        if new_mouse_position[1] > monitor.height:
            new_mouse_position[1] = monitor.height
    return new_mouse_position


def execute_calibrations(
    calibration_instructions: Iterator,
    on_finish: Callable,
    collected_vectors: List[Vector] = [],
):
    global temp_calibration_result
    next_instruction = next(calibration_instructions, None)
    if next_instruction is None:
        calibration_window.unset_calibration_point()
        calibration_window.unset_main_text()
        calibration_window.unset_image()
        temp_calibration_result = CalibrationResult(collected_vectors)
        tracking_approach.calibrate(temp_calibration_result)
        on_finish()
    else:
        execute_calibration(
            next_instruction,
            lambda vector: execute_calibrations(calibration_instructions, on_finish, collected_vectors + [vector]),
        )


def execute_calibration(calibration_instruction: CalibrationInstruction, on_finish: Callable[[Vector], None]):
    calibration_window.unset_calibration_point()
    calibration_window.unset_main_text()
    calibration_window.unset_image()

    vector = calibration_instruction.vector
    text = calibration_instruction.text
    image = calibration_instruction.image

    if vector is not None:
        calibration_window.set_calibration_point(scale_vector_to_screen(vector))
    if text is not None:
        calibration_window.set_main_text(text)
    if image is not None:
        calibration_window.set_image(image)

    end_time = datetime.now() + timedelta(
        seconds=config.WAIT_TIME_BEFORE_COLLECTING_VECTORS_IN_SEC + config.VECTOR_COLLECTION_TIME_IN_SEC
    )
    calibration_window.after(
        config.WAIT_TIME_BEFORE_COLLECTING_VECTORS_IN_SEC * 1000,
        collect_calibration_vectors,
        calibration_instruction,
        on_finish,
        end_time,
    )


def collect_calibration_vectors(
    calibration_instruction: CalibrationInstruction,
    on_finish: Callable[[Vector], None],
    end_time: datetime,
    vectors: List[Vector] = None,
):
    if vectors is None:
        vectors = []

    now = datetime.now()
    if now > end_time:
        on_finish(np.mean(np.array(vectors), axis=0) if len(vectors) > 0 else (0, 0))
    else:
        if last_input_method_vector is not None:
            vectors.append(last_input_method_vector)

        vector = calibration_instruction.vector
        text = calibration_instruction.text
        remaining_seconds = int((end_time - now).total_seconds())

        if vector is not None:
            calibration_window.set_calibration_point(scale_vector_to_screen(vector), str(remaining_seconds))
        elif text is not None:
            calibration_window.set_main_text(text + f" ... {remaining_seconds}")
        else:
            calibration_window.set_main_text(str(remaining_seconds))

        calibration_window.after(
            config.LOOP_SLEEP_IN_MILLISEC,
            collect_calibration_vectors,
            calibration_instruction,
            on_finish,
            end_time,
            vectors,
        )


main_menu_window = MainMenuWindow()
root_window = main_menu_window.get_window()
show_release_notes_if_needed(root_window)
root_window.protocol("WM_DELETE_WINDOW", on_close)
root_window.after(0, poll_ui)

reload_input_method(args.input_method, root_window)
reload_tracking_approach(args.tracking_approach)
reload_output_method(args.output_method, root_window)
reload_calibration_result()

main_menu_window.set_input_method_options(input_methods)
main_menu_window.set_current_input_method(selected_input_method)
main_menu_window.on_input_method_change_requested(
    lambda new_input_method: (reload_input_method(new_input_method, root_window), reload_calibration_result())
)

main_menu_window.set_tracking_approach_options(tracking_approaches)
main_menu_window.set_current_tracking_approach(selected_tracking_approach)
main_menu_window.on_tracking_approach_change_requested(
    lambda new_tracking_approach: (reload_tracking_approach(new_tracking_approach), reload_calibration_result())
)

main_menu_window.set_output_method_options(output_methods)
main_menu_window.set_current_output_method(selected_output_method)
main_menu_window.on_output_method_change_requested(
    lambda new_output_method: reload_output_method(new_output_method, root_window)
)

main_menu_window.on_calibration_requested(on_calibration_requested)

request_loop = Thread(target=loop, daemon=True)
request_loop.start()

main_menu_window.mainloop()

stop_event.set()
request_loop.join(timeout=1)

try:
    if input_method is not None:
        input_method.stop()
except Exception:
    traceback.print_exc()

try:
    if output_method is not None:
        output_method.stop()
except Exception:
    traceback.print_exc()

logger.info("bye")
