import flet as ft

from checks import (
    is_antivirus_installed,
    is_antivirus_operational,
    is_firewall_installed,
    is_firewall_operational,
    is_internet_connected,
)
from models import SecurityCheckResult


def make_group(title: str, content: ft.Control) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(title, weight=ft.FontWeight.BOLD, size=13),
                content,
            ],
            spacing=6,
        ),
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=6,
        padding=10,
    )


def make_row(button: ft.Control, field: ft.Control) -> ft.Row:
    return ft.Row([button, field], spacing=10)


def main(page: ft.Page) -> None:
    page.title = "Программа проверки информационной безопасности"
    page.window.width = 650
    page.window.height = 500
    page.window.resizable = False

    result = SecurityCheckResult()

    # --- TextFields ---
    tf_internet = ft.TextField(read_only=True, expand=True, height=38)
    tf_fw_installed = ft.TextField(read_only=True, expand=True, height=38)
    tf_fw_operational = ft.TextField(read_only=True, expand=True, height=38)
    tf_av_installed = ft.TextField(read_only=True, expand=True, height=38)
    tf_av_operational = ft.TextField(read_only=True, expand=True, height=38)
    results_area = ft.TextField(
        read_only=True,
        multiline=True,
        expand=True,
        min_lines=6,
    )

    def _bool_text(value: bool, true_text: str, false_text: str) -> str:
        return true_text if value else false_text

    # --- Check handlers ---
    def check_internet(e):
        value = is_internet_connected()
        result.internet_connected = value
        tf_internet.value = _bool_text(value, "Подключён", "Не подключён")
        page.update()

    def check_fw_installed(e):
        value = is_firewall_installed()
        result.firewall_installed = value
        tf_fw_installed.value = _bool_text(value, "Установлен", "Не установлен")
        page.update()

    def check_fw_operational(e):
        value = is_firewall_operational()
        result.firewall_operational = value
        tf_fw_operational.value = _bool_text(value, "Активен", "Неактивен")
        page.update()

    def check_av_installed(e):
        value = is_antivirus_installed()
        result.antivirus_installed = value
        tf_av_installed.value = value if value is not None else "Не установлен"
        page.update()

    def check_av_operational(e):
        value = is_antivirus_operational()
        result.antivirus_operational = value
        tf_av_operational.value = _bool_text(
            value, "Защита включена", "Защита отключена"
        )
        page.update()

    def _format_field(label: str, value) -> str:
        if value is None:
            status = "не выполнялось"
        elif value:
            status = "Да / активно"
        else:
            status = "Нет / неактивно"
        return f"{label}: {status}"

    def show_results(e):
        lines = [
            _format_field("Интернет подключён", result.internet_connected),
            _format_field("Межсетевой экран установлен", result.firewall_installed),
            _format_field("Межсетевой экран активен", result.firewall_operational),
            f"Антивирус установлен: {result.antivirus_installed if result.antivirus_installed is not None else 'не выполнялось'}",
            _format_field(
                "Антивирус активен (защита в реальном времени)",
                result.antivirus_operational,
            ),
        ]
        results_area.value = "\n".join(lines)

        # Reset individual fields and state
        for tf in (
            tf_internet,
            tf_fw_installed,
            tf_fw_operational,
            tf_av_installed,
            tf_av_operational,
        ):
            tf.value = ""

        # Reset result object in-place
        result.internet_connected = None
        result.firewall_installed = None
        result.antivirus_installed = None
        result.firewall_operational = None
        result.antivirus_operational = None

        page.update()

    def save_results(e):
        with open("results.txt", "w", encoding="utf-8") as f:
            f.write(results_area.value or "")

    def exit_app(e):
        page.window.close()

    # --- Buttons ---
    btn_w = 230

    btn_internet = ft.ElevatedButton(
        "Проверить интернет-соединение", width=btn_w, on_click=check_internet
    )
    btn_fw_installed = ft.ElevatedButton(
        "Проверить наличие МЭ", width=btn_w, on_click=check_fw_installed
    )
    btn_fw_operational = ft.ElevatedButton(
        "Проверить работу МЭ", width=btn_w, on_click=check_fw_operational
    )
    btn_av_installed = ft.ElevatedButton(
        "Проверить наличие АВ", width=btn_w, on_click=check_av_installed
    )
    btn_av_operational = ft.ElevatedButton(
        "Проверить работу АВ", width=btn_w, on_click=check_av_operational
    )

    # --- Groups ---
    firewall_group = make_group(
        "Проверка межсетевого экрана",
        ft.Column(
            [
                make_row(btn_internet, tf_internet),
                make_row(btn_fw_installed, tf_fw_installed),
                make_row(btn_fw_operational, tf_fw_operational),
            ],
            spacing=6,
        ),
    )

    antivirus_group = make_group(
        "Проверка антивирусного ПО",
        ft.Column(
            [
                make_row(btn_av_installed, tf_av_installed),
                make_row(btn_av_operational, tf_av_operational),
            ],
            spacing=6,
        ),
    )

    results_group = make_group(
        "Результаты проверок и рекомендации",
        results_area,
    )

    action_row = ft.Row(
        [
            ft.ElevatedButton("Вывести результаты", on_click=show_results),
            ft.ElevatedButton("Сохранить результаты в файл", on_click=save_results),
            ft.ElevatedButton("Выход", on_click=exit_app),
        ],
        alignment=ft.MainAxisAlignment.END,
        spacing=8,
    )

    page.add(
        ft.Column(
            [
                firewall_group,
                antivirus_group,
                results_group,
                action_row,
            ],
            spacing=10,
            expand=True,
        )
    )


ft.app(target=main)
