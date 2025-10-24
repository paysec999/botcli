import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.box import DOUBLE
from rich.syntax import Syntax
import re

# ANSI color codes for responses
GREEN = '\033[32m'
RED = '\033[31m'
YELLOW = '\033[33m'
CYAN = '\033[36m'
RESET = '\033[0m'

class ChatCommand:
    def __init__(self, gemini_service):
        self.gemini_service = gemini_service
        self.console = Console()

    def execute(self, args):
        if args:
            # If message provided via args, process it directly
            user_input = ' '.join(args)
            self.process_command(user_input)
        else:
            # Interactive chat mode
            self.interactive_chat()

    def interactive_chat(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        # Get weather information
        weather_response = self.gemini_service.get_weather("Denpasar")
        weather_section = ""
        border_color = "red"  # Default border color

        if weather_response["reply"]:
            weather_data = weather_response["reply"]
            emoji = weather_data["emoji"]
            color = weather_data["color"]
            weather_section = f"""
[bold {color}]Cuaca Denpasar {emoji}:[/bold {color}]
• Kondisi: {weather_data["description"]}
• Suhu: {weather_data["temp"]}°C
• Kelembaban: {weather_data["humidity"]}%
• Angin: {weather_data["wind_speed"]} m/s"""
            # Change border color based on weather
            if color == "yellow":
                border_color = "yellow"
            elif color == "blue":
                border_color = "blue"
            elif color == "purple":
                border_color = "purple"
            elif color == "cyan":
                border_color = "cyan"
            elif color == "white":
                border_color = "white"
        elif weather_response["error"]:
            weather_section = f"\n\n[bold yellow]Cuaca:[/bold yellow]\n[red]Tidak dapat mengambil data cuaca[/red]"

        # Create a panel for the header
        header_content = f"""[yellow]##DITBOT CLI V0.0.2[/yellow]
Selamat datang kembali "radit"
Ruang Kerja: {os.getcwd()}{weather_section}
Tips: ketik /help atau "exit" untuk keluar"""

        header_panel = Panel.fit(
            header_content,
            title="[bold red]DITBOT[/bold red]",
            border_style=border_color,
            box=DOUBLE
        )

        self.console.print(header_panel)
        self.console.print()

        while True:
            try:
                user_input = input(f"{CYAN}> {RESET}").strip()
                if user_input.lower() == 'exit':
                    goodbye_panel = Panel.fit(
                        "[green]Selamat tinggal, Radit! 👋[/green]",
                        title="[bold yellow]Keluar[/bold yellow]",
                        border_style="yellow",
                        box=DOUBLE
                    )
                    self.console.print(goodbye_panel)
                    self.gemini_service.save_history()
                    break

                if not self.process_command(user_input):
                    break
            except KeyboardInterrupt:
                goodbye_panel = Panel.fit(
                    "[green]Selamat tinggal, Radit! 👋[/green]",
                    title="[bold yellow]Keluar[/bold yellow]",
                    border_style="yellow",
                    box=DOUBLE
                )
                self.console.print(goodbye_panel)
                self.gemini_service.save_history()
                break

    def process_command(self, user_input):
        lower_input = user_input.lower()
        if user_input == '/save':
            self.gemini_service.save_history()
            success_panel = Panel.fit(
                "[green]Riwayat percakapan berhasil disimpan![/green]",
                title="[bold blue]Simpan[/bold blue]",
                border_style="blue",
                box=DOUBLE
            )
            self.console.print(success_panel)
            return True
        elif user_input == '/load':
            self.gemini_service.messages = self.gemini_service.load_history()
            success_panel = Panel.fit(
                "[green]Riwayat percakapan berhasil dimuat![/green]",
                title="[bold blue]Muat[/bold blue]",
                border_style="blue",
                box=DOUBLE
            )
            self.console.print(success_panel)
            return True
        elif 'buatkan code' in lower_input or 'buat code' in lower_input or 'generate code' in lower_input or 'buat program' in lower_input or 'buat aplikasi' in lower_input:
            # Extract description after the keyword
            keywords = ['buatkan code', 'buat code', 'generate code', 'buat program', 'buat aplikasi']
            found_keyword = None
            for kw in keywords:
                if kw in lower_input:
                    found_keyword = kw
                    break
            if found_keyword:
                code_prompt = user_input[user_input.lower().find(found_keyword) + len(found_keyword):].strip()
            else:
                code_prompt = user_input
            if not code_prompt:
                error_panel = Panel.fit(
                    "[red]Error: Masukkan deskripsi setelah 'buatkan code', contoh: buatkan code untuk permainan tictactoe dengan python[/red]",
                    title="[bold red]Error[/bold red]",
                    border_style="red",
                    box=DOUBLE
                )
                self.console.print(error_panel)
                return True
            response = self.gemini_service.generate_code(code_prompt)
            self.display_response(response, "Gemini (Code)")
            # Offer to save the code to a file
            if not response.get('error'):
                self.offer_save_code(response['reply'])
            return True
        elif 'analisis' in lower_input or 'analyze' in lower_input or 'periksa' in lower_input or 'cek' in lower_input:
            # Extract file path
            keywords = ['analisis', 'analyze', 'periksa', 'cek']
            found_keyword = None
            for kw in keywords:
                if kw in lower_input:
                    found_keyword = kw
                    break
            if found_keyword:
                file_path = user_input[user_input.lower().find(found_keyword) + len(found_keyword):].strip()
            else:
                file_path = user_input
            if not file_path:
                error_panel = Panel.fit(
                    "[red]Error: Masukkan path file setelah 'analisis', contoh: analisis file.py[/red]",
                    title="[bold red]Error[/bold red]",
                    border_style="red",
                    box=DOUBLE
                )
                self.console.print(error_panel)
                return True
            response = self.gemini_service.analyze_file(file_path)
            self.display_response(response, "Gemini (Analisis)")
            return True
        elif 'test' in lower_input or 'uji' in lower_input or 'testing' in lower_input:
            # Extract file path for testing
            keywords = ['test', 'uji', 'testing']
            found_keyword = None
            for kw in keywords:
                if kw in lower_input:
                    found_keyword = kw
                    break
            if found_keyword:
                file_path = user_input[user_input.lower().find(found_keyword) + len(found_keyword):].strip()
            else:
                file_path = user_input
            if not file_path:
                error_panel = Panel.fit(
                    "[red]Error: Masukkan path file setelah 'test', contoh: test file.py[/red]",
                    title="[bold red]Error[/bold red]",
                    border_style="red",
                    box=DOUBLE
                )
                self.console.print(error_panel)
                return True
            response = self.gemini_service.test_file(file_path)
            self.display_response(response, "Gemini (Testing)")
            return True
        elif 'debug' in lower_input or 'awakutu' in lower_input or 'perbaiki' in lower_input:
            # Extract file path and optional description for debugging
            keywords = ['debug', 'awakutu', 'perbaiki']
            found_keyword = None
            for kw in keywords:
                if kw in lower_input:
                    found_keyword = kw
                    break
            if found_keyword:
                remaining_text = user_input[user_input.lower().find(found_keyword) + len(found_keyword):].strip()
                # Split by common separators to get file path and description
                if ' dengan ' in remaining_text.lower():
                    parts = remaining_text.lower().split(' dengan ', 1)
                    file_path = parts[0].strip()
                    description = parts[1].strip()
                elif ' karena ' in remaining_text.lower():
                    parts = remaining_text.lower().split(' karena ', 1)
                    file_path = parts[0].strip()
                    description = parts[1].strip()
                else:
                    file_path = remaining_text
                    description = None
            else:
                file_path = user_input
                description = None
            if not file_path:
                error_panel = Panel.fit(
                    "[red]Error: Masukkan path file setelah 'debug', contoh: debug file.py[/red]",
                    title="[bold red]Error[/bold red]",
                    border_style="red",
                    box=DOUBLE
                )
                self.console.print(error_panel)
                return True
            response = self.gemini_service.debug_file(file_path, description)
            self.display_response(response, "Gemini (Debug)")
            return True
        elif 'kesehatan' in lower_input or 'health' in lower_input or 'istirahat' in lower_input or 'break' in lower_input:
            # Health and ergonomic advice
            keywords = ['kesehatan', 'health', 'istirahat', 'break']
            found_keyword = None
            for kw in keywords:
                if kw in lower_input:
                    found_keyword = kw
                    break
            if found_keyword:
                remaining_text = user_input[user_input.lower().find(found_keyword) + len(found_keyword):].strip()
                # Try to extract hours worked
                import re
                hours_match = re.search(r'(\d+)\s*(jam|hour|hours)', remaining_text.lower())
                if hours_match:
                    hours = int(hours_match.group(1))
                else:
                    hours = 2  # Default assumption
            else:
                hours = 2  # Default assumption
            response = self.gemini_service.get_health_advice(hours)
            self.display_response(response, "Gemini (Kesehatan)")
            return True
        elif 'backup' in lower_input or 'cadangkan' in lower_input:
            # Backup files
            keywords = ['backup', 'cadangkan']
            found_keyword = None
            for kw in keywords:
                if kw in lower_input:
                    found_keyword = kw
                    break
            if found_keyword:
                remaining_text = user_input[user_input.lower().find(found_keyword) + len(found_keyword):].strip()
                # Parse pattern and destination
                if ' ke ' in remaining_text.lower():
                    parts = remaining_text.lower().split(' ke ', 1)
                    pattern = parts[0].strip()
                    destination = parts[1].strip()
                else:
                    # Default pattern and destination
                    pattern = "*.py"
                    destination = "./backup"
            else:
                pattern = "*.py"
                destination = "./backup"
            response = self.gemini_service.backup_files(pattern, destination)
            if response["error"]:
                error_panel = Panel.fit(
                    f"[red]{response['error']}[/red]",
                    title="[bold red]Error Backup[/bold red]",
                    border_style="red",
                    box=DOUBLE
                )
                self.console.print(error_panel)
            else:
                success_panel = Panel.fit(
                    f"[green]{response['reply']}[/green]",
                    title="[bold green]Backup Berhasil[/bold green]",
                    border_style="green",
                    box=DOUBLE
                )
                self.console.print(success_panel)
            return True
        elif 'dashboard' in lower_input or 'ringkasan' in lower_input or 'aktivitas' in lower_input:
            # Activity dashboard
            response = self.gemini_service.get_activity_summary()
            self.display_response(response, "Dashboard Aktivitas")
            return True
        elif 'berita' in lower_input or 'news' in lower_input:
            # News summary
            keywords = ['berita', 'news']
            found_keyword = None
            for kw in keywords:
                if kw in lower_input:
                    found_keyword = kw
                    break
            if found_keyword:
                topic = user_input[user_input.lower().find(found_keyword) + len(found_keyword):].strip()
                if not topic:
                    topic = None
            else:
                topic = None
            response = self.gemini_service.get_news_summary(topic)
            self.display_response(response, "Berita Terkini")
            return True
        elif 'cuaca' in lower_input or 'weather' in lower_input:
            # Weather information
            keywords = ['cuaca', 'weather']
            found_keyword = None
            for kw in keywords:
                if kw in lower_input:
                    found_keyword = kw
                    break
            if found_keyword:
                city = user_input[user_input.lower().find(found_keyword) + len(found_keyword):].strip()
                if not city:
                    city = "Jakarta"
            else:
                city = "Jakarta"
            response = self.gemini_service.get_weather_info(city)
            self.display_response(response, f"Cuaca {city.title()}")
            return True
        elif 'rekomendasi' in lower_input or 'recommend' in lower_input:
            # Daily recommendations
            keywords = ['rekomendasi', 'recommend']
            found_keyword = None
            for kw in keywords:
                if kw in lower_input:
                    found_keyword = kw
                    break
            if found_keyword:
                category = user_input[user_input.lower().find(found_keyword) + len(found_keyword):].strip()
                if not category:
                    category = "music"
                # Extract category from common patterns
                if 'musik' in category.lower() or 'music' in category.lower():
                    category = "music"
                elif 'film' in category.lower() or 'movie' in category.lower():
                    category = "movie"
                elif 'resep' in category.lower() or 'recipe' in category.lower():
                    category = "recipe"
                else:
                    category = "music"  # default
            else:
                category = "music"
            response = self.gemini_service.get_daily_recommendations(category)
            self.display_response(response, f"Rekomendasi {category.title()}")
            return True
        elif 'hapus' in lower_input or 'delete' in lower_input:
            # Delete files
            keywords = ['hapus', 'delete']
            found_keyword = None
            for kw in keywords:
                if kw in lower_input:
                    found_keyword = kw
                    break
            if found_keyword:
                pattern = user_input[user_input.lower().find(found_keyword) + len(found_keyword):].strip()
                if not pattern:
                    error_panel = Panel.fit(
                        "[red]Error: Masukkan pola file setelah 'hapus', contoh: hapus *.tmp[/red]",
                        title="[bold red]Error[/bold red]",
                        border_style="red",
                        box=DOUBLE
                    )
                    self.console.print(error_panel)
                    return True
            else:
                pattern = user_input
            response = self.gemini_service.delete_files(pattern)
            self.display_response(response, "Penghapusan File")
            return True
        elif 'hitung' in lower_input or 'math' in lower_input or 'matematika' in lower_input or 'solve' in lower_input:
            # Solve math problems
            keywords = ['hitung', 'math', 'matematika', 'solve']
            found_keyword = None
            for kw in keywords:
                if kw in lower_input:
                    found_keyword = kw
                    break
            if found_keyword:
                problem = user_input[user_input.lower().find(found_keyword) + len(found_keyword):].strip()
                if not problem:
                    error_panel = Panel.fit(
                        "[red]Error: Masukkan soal matematika setelah 'hitung', contoh: hitung 2 + 2[/red]",
                        title="[bold red]Error[/bold red]",
                        border_style="red",
                        box=DOUBLE
                    )
                    self.console.print(error_panel)
                    return True
            else:
                problem = user_input
            response = self.gemini_service.solve_math_problem(problem)
            self.display_response(response, "Penyelesaian Matematika")
            return True
        elif 'terjemahkan' in lower_input or 'translate' in lower_input or 'ubah ke bahasa' in lower_input:
            # Parse for text and language
            keywords = ['terjemahkan', 'translate', 'ubah ke bahasa']
            found_keyword = None
            for kw in keywords:
                if kw in lower_input:
                    found_keyword = kw
                    break
            if found_keyword:
                after_keyword = user_input[user_input.lower().find(found_keyword) + len(found_keyword):].strip()
            else:
                after_keyword = user_input
            # Assume format: "text dalam bahasa lang" or "text to lang"
            if 'dalam bahasa' in after_keyword.lower():
                parts = after_keyword.split('dalam bahasa', 1)
                text = parts[0].strip()
                lang = parts[1].strip()
            elif 'to' in after_keyword.lower():
                parts = after_keyword.split('to', 1)
                text = parts[0].strip()
                lang = parts[1].strip()
            elif 'ke bahasa' in after_keyword.lower():
                parts = after_keyword.split('ke bahasa', 1)
                text = parts[0].strip()
                lang = parts[1].strip()
            else:
                error_panel = Panel.fit(
                    "[red]Error: Format salah. Contoh: terjemahkan 'hello world' dalam bahasa indonesia[/red]",
                    title="[bold red]Error[/bold red]",
                    border_style="red",
                    box=DOUBLE
                )
                self.console.print(error_panel)
                return True
            if not text or not lang:
                error_panel = Panel.fit(
                    "[red]Error: Masukkan teks dan bahasa, contoh: terjemahkan 'hello' dalam bahasa indonesia[/red]",
                    title="[bold red]Error[/bold red]",
                    border_style="red",
                    box=DOUBLE
                )
                self.console.print(error_panel)
                return True
            response = self.gemini_service.translate_text(lang, text)
            self.display_response(response, "Gemini (Terjemahan)")
            return True
        elif user_input.startswith('/help'):
            self.show_help()
            return True
        else:
            # Normal chat
            response = self.gemini_service.send_message(user_input)
            self.display_response(response, "Gemini")
            return True

    def display_response(self, response, title):
        if response.get('error'):
            error_panel = Panel.fit(
                f"[red]{response['error']}[/red]",
                title=f"[bold red]{title}[/bold red]",
                border_style="red",
                box=DOUBLE
            )
            self.console.print(error_panel)
        else:
            reply = response.get('reply', 'No reply received.')
            self.tampilkan_dengan_format(reply, title)

    def tampilkan_dengan_format(self, teks, title):
        # Process markdown-style formatting
        teks = self.process_markdown_formatting(teks)

        # Deteksi blok kode ```python ... ```
        pattern = r"```(\w+)?\n(.*?)```"
        blocks = re.findall(pattern, teks, re.DOTALL)

        if not blocks:
            response_panel = Panel.fit(
                teks,
                title=f"[bold green]{title}[/bold green]",
                border_style="green",
                box=DOUBLE
            )
            self.console.print(response_panel)
            return

        # Tampilkan blok kode dengan highlight
        for lang, code in blocks:
            syntax = Syntax(code.strip(), lang or "python", theme="monokai", line_numbers=True)
            response_panel = Panel.fit(
                syntax,
                title=f"[bold green]{title}[/bold green]",
                border_style="green",
                box=DOUBLE
            )
            self.console.print(response_panel)

        # Kalau ada teks di luar blok kode
        teks_bersih = re.sub(pattern, "", teks, flags=re.DOTALL)
        if teks_bersih.strip():
            response_panel = Panel.fit(
                teks_bersih.strip(),
                title=f"[bold green]{title}[/bold green]",
                border_style="green",
                box=DOUBLE
            )
            self.console.print(response_panel)

    def process_markdown_formatting(self, text):
        """Convert markdown-style formatting to Rich markup"""
        # Convert **bold** to [bold]bold[/bold]
        text = re.sub(r'\*\*(.*?)\*\*', r'[bold]\1[/bold]', text)

        # Convert *italic* to [italic]italic[/italic]
        text = re.sub(r'\*(.*?)\*', r'[italic]\1[/italic]', text)

        # Handle bullet points with better formatting
        lines = text.split('\n')
        formatted_lines = []
        for line in lines:
            if line.strip().startswith('•'):
                # Make bullet points cyan
                formatted_lines.append(f"[cyan]{line}[/cyan]")
            else:
                formatted_lines.append(line)

        return '\n'.join(formatted_lines)


    def offer_save_code(self, code_text):
        # Extract code from markdown blocks
        pattern = r"```(\w+)?\n(.*?)```"
        blocks = re.findall(pattern, code_text, re.DOTALL)
        if not blocks:
            return

        # Take the first code block
        lang, code = blocks[0]
        filename = f"generated_code.{lang or 'txt'}"

        # Ask user if they want to save
        save_prompt = Panel.fit(
            f"[yellow]Apakah Anda ingin menyimpan kode ke file '{filename}'? (y/n)[/yellow]",
            title="[bold blue]Save Code[/bold blue]",
            border_style="blue",
            box=DOUBLE
        )
        self.console.print(save_prompt)

        try:
            answer = input(f"{CYAN}> {RESET}").strip().lower()
            if answer in ['y', 'yes', 'ya']:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code.strip())
                success_panel = Panel.fit(
                    f"[green]Kode berhasil disimpan ke '{filename}'[/green]",
                    title="[bold green]Saved[/bold green]",
                    border_style="green",
                    box=DOUBLE
                )
                self.console.print(success_panel)
        except KeyboardInterrupt:
            pass

    def show_help(self):
        help_content = """[bold yellow]Perintah yang tersedia:[/bold yellow]

[cyan]buatkan/terjemahkan/analisis/test/debug/kesehatan/backup/dashboard/berita/cuaca/rekomendasi [teks][/cyan]

[cyan]buatkan code/program/aplikasi <deskripsi>[/cyan] - Buat kode berdasarkan deskripsi
[cyan]analisis/periksa/cek <file_path>[/cyan]         - Analisis teks dari file
[cyan]test/uji/testing <file_path>[/cyan]            - Berikan rekomendasi testing untuk file
[cyan]debug/awakutu/perbaiki <file_path> [dengan/karena <deskripsi>][/cyan] - Debug file dengan deskripsi opsional
[cyan]kesehatan/health/istirahat/break [jam][/cyan]  - Saran kesehatan dan ergonomis
[cyan]backup/cadangkan <pattern> ke <destination>[/cyan] - Backup file berdasarkan pola
[cyan]dashboard/ringkasan/aktivitas[/cyan]           - Tampilkan dashboard ringkasan aktivitas
[cyan]berita/news [topik][/cyan]                     - Ringkasan berita terkini
[cyan]cuaca/weather [kota][/cyan]                    - Informasi cuaca saat ini
[cyan]rekomendasi/recommend [kategori][/cyan]        - Rekomendasi harian (musik/film/resep)
[cyan]hapus/delete <pola_file>[/cyan]                - Hapus file berdasarkan pola (contoh: *.tmp)
[cyan]hitung/math/matematika/solve <soal>[/cyan]     - Selesaikan soal matematika
[cyan]terjemahkan/ubah ke bahasa <teks> dalam bahasa <bahasa>[/cyan] - Terjemahkan teks
[cyan]/save[/cyan]                                   - Simpan riwayat percakapan
[cyan]/load[/cyan]                                   - Muat riwayat percakapan
[cyan]/help[/cyan]                                   - Tampilkan pesan bantuan
[cyan]exit[/cyan]                                    - Keluar dari obrolan

[bold yellow]Contoh penggunaan:[/bold yellow]
[cyan]buatkan code untuk permainan tictactoe dengan python[/cyan]
[cyan]analisis main.py[/cyan]
[cyan]terjemahkan 'hello world' dalam bahasa indonesia[/cyan]
[cyan]test tictactoe.py[/cyan]
[cyan]debug main.py dengan error index out of range[/cyan]
[cyan]kesehatan 3 jam[/cyan]
[cyan]backup *.py ke ./backup[/cyan]
[cyan]dashboard[/cyan]                               - Lihat ringkasan aktivitas hari ini
[cyan]berita teknologi[/cyan]                        - Berita tentang teknologi
[cyan]cuaca Jakarta[/cyan]                           - Cuaca di Jakarta
[cyan]rekomendasi musik[/cyan]                       - Rekomendasi playlist musik
[cyan]hapus *.tmp[/cyan]                             - Hapus semua file .tmp
[cyan]delete test_*.py[/cyan]                        - Hapus file Python yang dimulai dengan test_
[cyan]hitung 2 + 2 * 3[/cyan]                        - Hitung operasi matematika
[cyan]math solve quadratic equation[/cyan]           - Selesaikan persamaan kuadrat
[cyan]buat program kalkulator sederhana[/cyan]
[cyan]periksa requirements.txt[/cyan]"""

        help_panel = Panel.fit(
            help_content,
            title="[bold green]Bantuan[/bold green]",
            border_style="green",
            box=DOUBLE
        )

        self.console.print(help_panel)

    def start_chat(self, user_input):
        response = self.gemini_service.send_message(user_input)
        return response

    def handle_response(self, response):
        if response.get('error'):
            return f"Error: {response['error']}"
        return response.get('reply', "No reply received.")
