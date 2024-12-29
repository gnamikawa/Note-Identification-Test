from functools import lru_cache
from music21 import stream, note, environment
from PIL import Image, ImageTk
import os

from config import Config


class NoteImageManager:
    TEMP_DIR = "note_cache"

    @staticmethod
    def get_image_path(note_name: str) -> str:
        """Get the file path for the note image.

        Args:
            note_name (str): The name of the note.

        Returns:
            str: The file path for the note image.
        """
        if not os.path.exists(NoteImageManager.TEMP_DIR):
            os.makedirs(NoteImageManager.TEMP_DIR)
        return os.path.join(NoteImageManager.TEMP_DIR, f"{note_name}.png")

    @staticmethod
    @lru_cache(maxsize=128)
    def render_note_image(note_name: str) -> ImageTk.PhotoImage:
        """Render the note image and return it as a PhotoImage.

        Args:
            note_name (str): The name of the note.

        Returns:
            ImageTk.PhotoImage: The rendered note image.
        """
        try:
            image_path = NoteImageManager.get_image_path(note_name)

            if not os.path.exists(image_path):
                s = stream.Stream()
                n = note.Note(note_name)
                s.append(n)
                s.write(fmt="musicxml.png", fp=image_path)

                # Rename the generated file to the desired name
                generated_image_path = image_path.replace(".png", "-1.png")
                if os.path.exists(generated_image_path):
                    os.rename(generated_image_path, image_path)

                # Delete the musicxml file
                musicxml_path = image_path.replace(".png", ".musicxml")
                if os.path.exists(musicxml_path):
                    os.remove(musicxml_path)

            image = Image.open(image_path)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            raise ValueError(f"The note '{note_name}' could not be rendered: {e}")

    @staticmethod
    def clean_up_musicxml_files() -> None:
        """Clean up old MusicXML files and temporary images."""
        for file in os.listdir(NoteImageManager.TEMP_DIR):
            if file.endswith(".musicxml") or file.endswith("-1.png"):
                os.remove(os.path.join(NoteImageManager.TEMP_DIR, file))

    @staticmethod
    def regenerate_missing_notes() -> None:
        """Regenerate missing note images."""
        for note in Config.NOTE_TO_MIDI.keys():
            image_path = NoteImageManager.get_image_path(note)
            if not os.path.exists(image_path):
                NoteImageManager.render_note_image(note)
