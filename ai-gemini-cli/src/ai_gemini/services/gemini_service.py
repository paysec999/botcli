import os
import json
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, InvalidArgument, PermissionDenied
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("API key not provided and GEMINI_API_KEY not set in environment")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.chat = None
        self.history_file = 'chat_history.json'
        self.messages = self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []

    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.messages, f)

    def send_message(self, message):
        try:
            if self.chat is None:
                self.chat = self.model.start_chat(history=self.messages[:-1] if self.messages else [])
            response = self.chat.send_message(message)
            assistant_response = response.text
            self.messages.append({'role': 'user', 'parts': [message]})
            self.messages.append({'role': 'model', 'parts': [assistant_response]})
            return {"reply": assistant_response, "error": None}
        except ResourceExhausted:
            return {"reply": None, "error": "Rate limit exceeded. Please try again later."}
        except InvalidArgument:
            return {"reply": None, "error": "Invalid input."}
        except PermissionDenied:
            return {"reply": None, "error": "API key or permissions issue."}
        except Exception as e:
            return {"reply": None, "error": str(e)}

    def generate_code(self, prompt):
        full_prompt = f"Generate code for: {prompt}. Provide clean, executable code with comments."
        return self.send_message(full_prompt)

    def analyze_file(self, file_path):
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                prompt = f"Analyze this text: {content[:1000]}"  # Limit to 1000 chars
                return self.send_message(prompt)
            except Exception as e:
                return {"reply": None, "error": f"Failed to read or analyze file: {str(e)}"}
        else:
            return {"reply": None, "error": "File not found."}

    def translate_text(self, lang, text):
        prompt = f"Translate to {lang}: {text}"
        return self.send_message(prompt)

    def test_file(self, file_path):
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                prompt = f"""Analyze this code file and provide testing recommendations. Include:
1. Unit tests that should be written
2. Integration tests if applicable
3. Edge cases to consider
4. Any potential bugs or issues

File: {file_path}
Content:
{content}"""
                return self.send_message(prompt)
            except Exception as e:
                return {"reply": None, "error": f"Failed to read or analyze file: {str(e)}"}
        else:
            return {"reply": None, "error": "File not found."}

    def debug_file(self, file_path, description=None):
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                prompt = f"""Debug this code file. Provide debugging recommendations and fixes for any issues found.

File: {file_path}
Content:
{content}"""
                if description:
                    prompt += f"\n\nAdditional description: {description}"
                prompt += """

Include:
1. Potential bugs or errors
2. Suggested fixes
3. Debugging steps
4. Best practices improvements"""
                return self.send_message(prompt)
            except Exception as e:
                return {"reply": None, "error": f"Failed to read or debug file: {str(e)}"}
        else:
            return {"reply": None, "error": "File not found."}

    def get_health_advice(self, hours_worked):
        prompt = f"""Provide health and ergonomic advice for someone who has been working at a computer for {hours_worked} hours. Include:
1. Break recommendations
2. Simple exercises or stretches
3. Ergonomic tips
4. Eye care suggestions
5. General wellness advice

Keep it concise and practical."""
        return self.send_message(prompt)

    def backup_files(self, pattern, destination):
        import shutil
        import glob
        try:
            files = glob.glob(pattern)
            if not files:
                return {"reply": None, "error": f"No files found matching pattern: {pattern}"}

            os.makedirs(destination, exist_ok=True)
            backed_up = []
            for file in files:
                if os.path.isfile(file):
                    shutil.copy2(file, destination)
                    backed_up.append(os.path.basename(file))

            return {"reply": f"Successfully backed up {len(backed_up)} files to {destination}: {', '.join(backed_up)}", "error": None}
        except Exception as e:
            return {"reply": None, "error": f"Backup failed: {str(e)}"}

    def get_weather(self, city="Denpasar"):
        import requests
        api_key = os.getenv('OPENWEATHER_API_KEY')
        if not api_key:
            return {"reply": None, "error": "OpenWeather API key not found. Please set OPENWEATHER_API_KEY in your .env file."}

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=id"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            weather_desc = data['weather'][0]['description']
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            weather_main = data['weather'][0]['main'].lower()

            # Determine weather emoji and color based on condition
            if 'clear' in weather_main:
                emoji = "☀️"
                color = "yellow"
            elif 'cloud' in weather_main:
                emoji = "☁️"
                color = "white"
            elif 'rain' in weather_main or 'drizzle' in weather_main:
                emoji = "🌧️"
                color = "blue"
            elif 'thunderstorm' in weather_main:
                emoji = "⛈️"
                color = "purple"
            elif 'snow' in weather_main:
                emoji = "❄️"
                color = "cyan"
            elif 'mist' in weather_main or 'fog' in weather_main:
                emoji = "🌫️"
                color = "grey"
            else:
                emoji = "🌤️"
                color = "green"

            weather_info = {
                "description": weather_desc.capitalize(),
                "temp": temp,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "emoji": emoji,
                "color": color
            }

            return {"reply": weather_info, "error": None}
        except requests.exceptions.RequestException as e:
            return {"reply": None, "error": f"Failed to fetch weather data: {str(e)}"}
        except KeyError as e:
            return {"reply": None, "error": f"Invalid weather data format: {str(e)}"}

    def get_activity_summary(self):
        import time
        import random
        # Simulate activity data (in a real implementation, this would track actual usage)
        activities = {
            'debugging': random.randint(20, 50),
            'coding': random.randint(15, 40),
            'testing': random.randint(10, 25),
            'documentation': random.randint(5, 15),
            'meetings': random.randint(5, 20),
            'learning': random.randint(5, 15)
        }

        # Normalize to 100%
        total = sum(activities.values())
        if total > 0:
            activities = {k: (v / total) * 100 for k, v in activities.items()}

        # Create ASCII bar chart
        def create_bar_chart(data, width=40):
            chart = []
            max_value = max(data.values())
            for activity, percentage in data.items():
                bar_length = int((percentage / 100) * width)
                bar = '█' * bar_length
                spaces = ' ' * (width - bar_length)
                chart.append(f"{activity.capitalize():<12}: [{bar}{spaces}] {percentage:.1f}%")
            return '\n'.join(chart)

        # Generate summary text
        top_activity = max(activities.items(), key=lambda x: x[1])
        summary = f"""📊 **Ringkasan Aktivitas Hari Ini**

🏆 **Aktivitas utama:** {top_activity[0].capitalize()} ({top_activity[1]:.1f}%)

📋 **Grafik Aktivitas:**
{create_bar_chart(activities)}

📈 **Detail Aktivitas:**
"""

        for activity, percentage in sorted(activities.items(), key=lambda x: x[1], reverse=True):
            summary += f"• {activity.capitalize()}: {percentage:.1f}%\n"

        summary += f"""
💡 **Rekomendasi:**
• Fokuskan lebih banyak waktu pada {top_activity[0]} jika produktivitas rendah
• Pastikan keseimbangan antara coding dan testing
• Jangan lupa istirahat setiap 1-2 jam

⏰ **Waktu kerja total:** {random.randint(4, 10)} jam hari ini"""

        return {"reply": summary, "error": None}

    def solve_math_problem(self, problem):
        """Solve mathematical problems using Gemini AI"""
        try:
            prompt = f"""Selesaikan soal matematika berikut dengan langkah-langkah yang jelas dan detail. Berikan jawaban akhir yang tepat.

Soal: {problem}

Format jawaban:
1. **Langkah-langkah penyelesaian:**
   - Langkah 1...
   - Langkah 2...
   - dst.

2. **Jawaban akhir:** [hasil]"""

            response = self.model.generate_content(prompt)
            return {"reply": response.text, "error": None}
        except Exception as e:
            return {"reply": None, "error": f"Gagal menyelesaikan soal matematika: {str(e)}"}

    def delete_files(self, pattern):
        import glob
        import os
        try:
            files = glob.glob(pattern)
            if not files:
                return {"reply": None, "error": f"Tidak ada file yang cocok dengan pola: {pattern}"}

            deleted = []
            for file in files:
                if os.path.isfile(file):
                    os.remove(file)
                    deleted.append(os.path.basename(file))

            if deleted:
                return {"reply": f"Berhasil menghapus {len(deleted)} file: {', '.join(deleted)}", "error": None}
            else:
                return {"reply": None, "error": f"Tidak ada file yang dapat dihapus dengan pola: {pattern}"}
        except Exception as e:
            return {"reply": None, "error": f"Gagal menghapus file: {str(e)}"}

    def get_news_summary(self, topic=None):
        # Use Gemini to generate a news summary (in real implementation, integrate with NewsAPI)
        if topic:
            prompt = f"Berikan ringkasan berita terkini tentang {topic} dalam bahasa Indonesia. Buat ringkas dan informatif."
        else:
            prompt = "Berikan ringkasan berita terkini dunia dan Indonesia dalam bahasa Indonesia. Fokus pada 3-5 berita utama."

        return self.send_message(prompt)

    def get_weather_info(self, city="Jakarta"):
        # Enhanced weather function for any city
        import requests
        api_key = os.getenv('OPENWEATHER_API_KEY')
        if not api_key:
            return {"reply": None, "error": "OpenWeather API key not found. Please set OPENWEATHER_API_KEY in your .env file."}

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=id"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            weather_desc = data['weather'][0]['description']
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            weather_main = data['weather'][0]['main'].lower()

            # Determine weather emoji and color based on condition
            if 'clear' in weather_main:
                emoji = "☀️"
                color = "yellow"
            elif 'cloud' in weather_main:
                emoji = "☁️"
                color = "white"
            elif 'rain' in weather_main or 'drizzle' in weather_main:
                emoji = "🌧️"
                color = "blue"
            elif 'thunderstorm' in weather_main:
                emoji = "⛈️"
                color = "purple"
            elif 'snow' in weather_main:
                emoji = "❄️"
                color = "cyan"
            elif 'mist' in weather_main or 'fog' in weather_main:
                emoji = "🌫️"
                color = "grey"
            else:
                emoji = "🌤️"
                color = "green"

            weather_info = f"""🌤️ **Cuaca di {city} {emoji}**

🌡️ **Kondisi:** {weather_desc.capitalize()}
🌡️ **Suhu:** {temp}°C
💧 **Kelembaban:** {humidity}%
💨 **Angin:** {wind_speed} m/s

💡 **Rekomendasi:** {'Bawa payung jika hujan ☂️' if 'rain' in weather_main else 'Nikmati hari yang cerah! 😎' if 'clear' in weather_main else 'Hati-hati di jalan 🛣️'}"""

            return {"reply": weather_info, "error": None}
        except requests.exceptions.RequestException as e:
            return {"reply": None, "error": f"Failed to fetch weather data: {str(e)}"}
        except KeyError as e:
            return {"reply": None, "error": f"Invalid weather data format: {str(e)}"}

    def get_daily_recommendations(self, category="music"):
        if category.lower() == "music" or category.lower() == "musik":
            prompt = """Rekomendasikan playlist musik untuk bekerja produktif. Berikan:
1. 5-7 lagu dengan artis
2. Genre yang cocok
3. Mengapa cocok untuk bekerja
4. Link Spotify jika memungkinkan

Buat dalam format yang menarik dan bahasa Indonesia."""
        elif category.lower() == "movie" or category.lower() == "film":
            prompt = """Rekomendasikan film menarik untuk ditonton hari ini. Berikan:
1. 3 film dengan sinopsis singkat
2. Genre dan rating
3. Mengapa direkomendasikan
4. Platform streaming jika tersedia

Fokus pada film terbaru atau klasik yang bagus."""
        elif category.lower() == "recipe" or category.lower() == "resep":
            prompt = """Rekomendasikan resep masakan sederhana untuk hari ini. Berikan:
1. Nama resep
2. Bahan-bahan utama
3. Langkah-langkah singkat
4. Waktu memasak
5. Tips penyajian

Pilih resep yang mudah dan sehat."""
        else:
            prompt = f"Rekomendasikan {category} menarik untuk hari ini dalam bahasa Indonesia."

        return self.send_message(prompt)

    def get_market_data(self):
        # Placeholder for market data
        pass

    def place_order(self, order_type, amount, price):
        # Placeholder for placing order
        pass

    def get_order_status(self, order_id):
        # Placeholder for order status
        pass
