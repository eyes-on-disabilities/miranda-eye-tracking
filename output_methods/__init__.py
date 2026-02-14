from output_methods.udp_output_method import UdpOutputMethod
from misc import resource_path
from guis.tkinter.main_menu_window import MainMenuOption
from output_methods.mouse_output_method import MouseOutputMethod
from output_methods.tts_keyboard_output_method import TtsKeyboardOutputMethod

output_methods: dict[MainMenuOption] = {
    "udp": MainMenuOption(
        key="udp",
        title="UDP-Export",
        description="Publish the gaze results over UDP in a simple JSON format.",
        icon=resource_path("assets/output_method_udp.png"),
        clazz=UdpOutputMethod,
    ),
    "mouse": MainMenuOption(
        key="mouse",
        title="Mouse Movement",
        description="Moves the mouse cursor according to the gaze.\nDoesn't work with the Mouse input.",
        icon=resource_path("assets/output_method_mouse.png"),
        clazz=MouseOutputMethod,
    ),
    "tts-keyboard": MainMenuOption(
        key="tts-keyboard",
        title="TTS Keyboard",
        description="A text-to-speech-keyboard.\n(Proove-of-concept)",
        icon=resource_path("assets/output_method_tts-keyboard.png"),
        clazz=TtsKeyboardOutputMethod,
    ),
}
