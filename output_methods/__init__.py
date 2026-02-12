from output_methods.udp_output_method import UdpPublisher
from misc import resource_path
from guis.tkinter.main_menu_window import MainMenuOption
from output_methods.mouse_output_method import MousePublisher
from output_methods.tts_keyboard_output_method import TtsKeyboardPublisher

output_methods: dict[MainMenuOption] = {
    "udp": MainMenuOption(
        key="udp",
        title="UDP-Publisher",
        description="Publish the gaze results over UDP in a simple JSON format.",
        icon=resource_path("assets/output_method_udp.png"),
        clazz=UdpPublisher,
    ),
    "mouse": MainMenuOption(
        key="mouse",
        title="Mouse Movement",
        description="Moves the mouse cursor according to the gaze.\nDoesn't work with the Mouse input method.",
        icon=resource_path("assets/output_method_mouse.png"),
        clazz=MousePublisher,
    ),
    "tts-keyboard": MainMenuOption(
        key="tts-keyboard",
        title="TTS Keyboard",
        description="A text-to-speech-keyboard.",
        icon=resource_path("assets/output_method_tts-keyboard.png"),
        clazz=TtsKeyboardPublisher,
    ),
}
