import threading
import logging
import tkinter as tk

logger = logging.getLogger("PosturaX.Interventions")


class InterventionManager:
    def __init__(self):
        self.overlay_root = None
        self.toast_root = None
        self._overlay_thread = None

    def dismiss_toast(self):
        """Safely closes any currently active toast/popup notification."""
        if self.toast_root is not None:
            try:
                self.toast_root.after(0, self.toast_root.destroy)
            except Exception as e:
                logger.error(f"Error dismissing toast: {e}")
            finally:
                self.toast_root = None

    def trigger_30s_toast(self):
        """30s Warning: Auto-dismisses in 5s or gets replaced by 60s notification."""
        self.dismiss_toast()  # Close existing toast if active

        def _show():
            try:
                self.toast_root = tk.Tk()
                self.toast_root.title("Posture Alert")
                self.toast_root.geometry("320x110+20+20")  # Top-left corner
                self.toast_root.attributes("-topmost", True)
                self.toast_root.configure(bg="#212121")

                label = tk.Label(
                    self.toast_root,
                    text="Posture Alert\n\nSit Straight!",
                    font=("Helvetica", 12, "bold"),
                    fg="white",
                    bg="#212121"
                )
                label.pack(expand=True)

                # Auto-dismiss strictly after 5 seconds (5000 ms)
                self.toast_root.after(5000, self.dismiss_toast)
                self.toast_root.mainloop()
            except Exception as e:
                logger.error(f"Error in 30s toast: {e}")
            finally:
                self.toast_root = None

        threading.Thread(target=_show, daemon=True).start()

    def trigger_60s_toast(self):
        """60s Warning: Dismisses on OK button OR when 90s overlay triggers."""
        self.dismiss_toast()  # Replaces 30s toast if still visible

        def _show():
            try:
                self.toast_root = tk.Tk()
                self.toast_root.title("Warning Alert")
                self.toast_root.geometry("360x140+20+20")
                self.toast_root.attributes("-topmost", True)
                self.toast_root.configure(bg="#B71C1C")

                label = tk.Label(
                    self.toast_root,
                    text="Warning Alert!\nContinuous slouching detected for 60 seconds.",
                    font=("Helvetica", 10, "bold"),
                    fg="white",
                    bg="#B71C1C",
                    wraplength=320
                )
                label.pack(pady=10)

                # OK Button to dismiss manually
                ok_btn = tk.Button(
                    self.toast_root,
                    text="OK",
                    font=("Helvetica", 10, "bold"),
                    command=self.dismiss_toast,
                    bg="white",
                    fg="#B71C1C",
                    width=10,
                    relief="flat"
                )
                ok_btn.pack(pady=5)

                self.toast_root.mainloop()
            except Exception as e:
                logger.error(f"Error in 60s toast: {e}")
            finally:
                self.toast_root = None

        threading.Thread(target=_show, daemon=True).start()

    def trigger_screen_overlay(self):
        """90s Overlay: Closes active toast and displays 60% white transparent screen lock."""
        self.dismiss_toast()  # Dismisses 60s toast before overlay appears

        if self.overlay_root is not None:
            return  # Already active

        def _run_gui():
            try:
                self.overlay_root = tk.Tk()
                self.overlay_root.title("PosturaX Overlay")
                self.overlay_root.attributes("-fullscreen", True)
                self.overlay_root.attributes("-topmost", True)
                
                # White color with 60% Transparency (0.6 opacity)
                self.overlay_root.attributes("-alpha", 0.6)
                self.overlay_root.configure(background="white")

                label = tk.Label(
                    self.overlay_root,
                    text="Posture Critical Alert!\n\nSit Straight to Dismiss Overlay",
                    font=("Helvetica", 32, "bold"),
                    fg="#111111",
                    bg="white",
                    justify="center"
                )
                label.pack(expand=True)

                self.overlay_root.mainloop()
            except Exception as e:
                logger.error(f"Error in screen overlay: {e}")
            finally:
                self.overlay_root = None

        self._overlay_thread = threading.Thread(target=_run_gui, daemon=True)
        self._overlay_thread.start()

    def dismiss_overlay(self):
        """Auto-dismisses overlay and all active popups when posture is restored."""
        self.dismiss_toast()
        if self.overlay_root is not None:
            try:
                self.overlay_root.after(0, self.overlay_root.destroy)
                logger.info("White screen overlay dismissed.")
            except Exception as e:
                logger.error(f"Error dismissing overlay: {e}")
            finally:
                self.overlay_root = None
