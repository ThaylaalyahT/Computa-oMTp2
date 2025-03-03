import flet as ft
from solitaire import Solitaire


def main(page: ft.Page):
    page.on_error = lambda e: print("Page error:", e.data)
    page.title = "solitaire"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    page.add(ft.Row([Solitaire()], alignment="center"))

ft.app(target=main, assets_dir="Images")