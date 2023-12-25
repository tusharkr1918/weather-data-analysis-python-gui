import os
import sys
import threading
import customtkinter as ctk
import webbrowser
from weather_forecast import analyze_and_plot
from api_manager import create_weather_api_table, save_api, fetch_data, load_from_json


class WeatherApp(ctk.CTk):
    current_user = {
        "user_name": "",
        "api_key": "d6e555e890f043ba8f5105021231912",
    }  # [default] ~ on adding new key, it will get removed.

    window_width = 825
    window_height = 410

    @staticmethod
    def resource_path(relative_path):
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def set_title(self, user_name):
        if user_name:
            title_text = f"{self.title()[:22]} ({user_name})"
            self.title(title_text)

    # noinspection PyTypeChecker
    def __init__(self, title, previous_data):
        super().__init__()
        WeatherApp.center_window(
            self, WeatherApp.window_width, WeatherApp.window_height
        )
        self.title(title)

        if previous_data:
            WeatherApp.current_user = previous_data

        self.location = None
        self.set_title(WeatherApp.current_user["user_name"])
        self.geometry(f"{self.window_width}x{self.window_height}")
        self.resizable(height=False, width=False)

        # Create a frame for the left section
        self.left_frame = ctk.CTkFrame(
            self, corner_radius=0, bg_color=("gray86", "grey11")
        )
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        self.text_field = ctk.CTkEntry(
            self.left_frame,
            placeholder_text="Insert Location",
            height=35,
            font=ctk.CTkFont(family="Century", size=16, weight="bold"),
        )

        self.text_field.grid(
            row=1, column=0, columnspan=2, sticky="ewn", padx=15, pady=(15, 5)
        )

        self.weather_box = ctk.CTkTextbox(
            self.left_frame, height=1, font=ctk.CTkFont(family="Constantia", size=15)
        )
        self.weather_box.configure(state="disabled")
        self.weather_box.grid(row=2, column=0, sticky="nsew", padx=(15, 5), pady=(0, 5))
        self.bind("<Return>", lambda event: self.update_app())
        self.button = ctk.CTkButton(
            self.left_frame,
            command=self.update_app,
            text="Search",
            width=17,
            height=30,
            font=ctk.CTkFont(family="Constantia", size=15),
        )

        self.button.grid(row=2, column=1, padx=(5, 15), pady=(0, 5), ipady=2)

        # Add an indeterminate progress bar below the button
        self.progress_bar = ctk.CTkProgressBar(
            self.left_frame, mode="determinate", height=3, progress_color="grey11"
        )
        self.progress_bar.set(1)
        self.progress_bar.grid(
            row=3, column=0, columnspan=2, sticky="we", pady=(5, 5), padx=15
        )

        self.bottom_box = ctk.CTkTextbox(
            self.left_frame, height=18, font=ctk.CTkFont(family="Constantia", size=14)
        )
        self.bottom_box.insert("0.0", "")
        self.bottom_box.configure(state="disabled", text_color=("red", "orange"))
        self.bottom_box.grid(
            row=4, column=0, columnspan=2, sticky="nsew", padx=15, pady=(5, 15)
        )
        # Set row weights
        self.left_frame.columnconfigure(0, weight=1)
        self.left_frame.rowconfigure(0, weight=0)
        self.left_frame.rowconfigure(1, weight=0)
        self.left_frame.rowconfigure(2, weight=0)
        self.left_frame.rowconfigure(3, weight=0)
        self.left_frame.rowconfigure(4, weight=1)

        # Create a frame for the right section with a fixed width
        self.right_frame = ctk.CTkFrame(self, width=500)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # Create a box in the right frame
        self.main_box = ctk.CTkLabel(self.right_frame)
        self.main_box.grid(row=0, column=0, sticky="nsew")

        self.rounded_frame = ctk.CTkLabel(
            self.main_box,
            width=530,
            height=360,
            bg_color="transparent",
            fg_color=("snow1", "gray11"),
            corner_radius=10,
            text="",
        )
        self.rounded_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=15)

        # Set column and row weights to make the frames expandable
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        # Create and grid the outer frame
        self.bottom_frame = ctk.CTkFrame(
            master=self, fg_color=("snow1", "grey11"), corner_radius=0
        )
        self.bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.hyperlink_to_api = ctk.CTkButton(
            self.bottom_frame,
            text="Don't have one? click here `weatherapi.com`",
            command=lambda: webbrowser.open("https://www.weatherapi.com"),
            hover_color="grey11",
            fg_color="transparent",
            font=ctk.CTkFont(family="Constantia", size=10, weight="bold"),
            height=10,
            text_color=("blue", "skyblue"),
        )
        self.hyperlink_to_api.grid(row=0, column=0, sticky="nws", padx=10, pady=2)

        # Create a button inside the frame and use grid
        self.api_btn = ctk.CTkButton(
            self.bottom_frame,
            text="MANAGE API KEYS",
            fg_color=("snow3", "gray26"),
            font=ctk.CTkFont(family="Constantia", size=10, weight="bold"),
            text_color=("grey11", "white"),
            corner_radius=5,
            command=self.open_api_manager,
            height=10,
            width=100,
        )
        self.api_btn.grid(row=0, column=1, sticky="news", padx=(466, 10), pady=2)

    @staticmethod
    def center_window(window, width, height):
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)

        # Set the geometry of the window to center it on the screen
        window.geometry("{}x{}+{}+{}".format(width, height, x, y))

    def add_tabview_frame(self):
        self.tabview_addbtn.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tabview_addbtn.grid_columnconfigure(0, weight=1)

        # Create widgets inside the frame
        self.add_status_label = ctk.CTkLabel(
            self.tabview_addbtn,
            text="",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            wraplength=240,
        )
        self.add_status_label.grid(sticky="nsew", padx=10)

        self.add_user_name = ctk.CTkEntry(
            self.tabview_addbtn,
            placeholder_text="Username",
            font=ctk.CTkFont(family="Constantia", size=15),
        )
        self.add_user_name.grid(sticky="nsew", pady=10)
        self.after(1000, lambda: self.add_user_name.focus_set())

        self.add_api_key = ctk.CTkEntry(
            self.tabview_addbtn,
            placeholder_text="API Key",
            font=ctk.CTkFont(family="Constantia", size=15),
        )
        self.add_api_key.grid(sticky="nsew", pady=(0, 10))

        self.add_password = ctk.CTkEntry(
            self.tabview_addbtn,
            placeholder_text="Password",
            font=ctk.CTkFont(family="Constantia", size=15),
        )
        self.add_password.grid(sticky="nsew", pady=(0, 10))

        self.add_submit = ctk.CTkButton(
            self.tabview_addbtn,
            text="Submit",
            command=lambda: self.add_status_label.configure(
                text=save_api(self.add_user_name, self.add_api_key, self.add_password)
            ),
            height=28,
            font=ctk.CTkFont(family="Constantia", size=15),
        )
        self.add_submit.grid(sticky="e")

    def load_tabview_frame(self):
        self.tabview_loadbtn.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tabview_loadbtn.grid_columnconfigure(0, weight=1)

        # Create widgets inside the frame
        self.load_status_label = ctk.CTkLabel(
            self.tabview_loadbtn,
            text="",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
        )
        self.load_status_label.grid(sticky="nsew", padx=10)

        self.load_user_name = ctk.CTkEntry(
            self.tabview_loadbtn,
            placeholder_text="Username",
            font=ctk.CTkFont(family="Constantia", size=15),
        )
        self.load_user_name.grid(sticky="nsew", pady=10)
        self.after(500, lambda: self.load_user_name.focus_set())

        self.load_password = ctk.CTkEntry(
            self.tabview_loadbtn,
            placeholder_text="Password",
            font=ctk.CTkFont(family="Constantia", size=15),
        )
        self.load_password.grid(sticky="nsew", pady=(0, 10))

        def fetch_data_wrapper():
            fetched_data = fetch_data(
                self.load_user_name, self.load_password, context=WeatherApp
            )
            self.load_status_label.configure(text=fetched_data[0])
            self.set_title(fetched_data[1])

        self.load_submit = ctk.CTkButton(
            self.tabview_loadbtn,
            text="Submit",
            command=lambda: fetch_data_wrapper(),
            height=28,
            font=ctk.CTkFont(family="Constantia", size=15),
        )
        self.load_submit.grid(sticky="e")

    def configure_api_manager_widgets(self):
        window_width = 350
        window_height = 350
        WeatherApp.center_window(self.top, window_width, window_height)

        self.top.title("Api Manager")
        self.top.resizable(height=False, width=False)

        # Adjusted row configuration weight
        self.top.grid_rowconfigure(1, weight=1)
        self.top.grid_columnconfigure(0, weight=1)

        self.api_label = ctk.CTkLabel(
            self.top,
            text="[Manage API keys]\nAdd a new key or load an existing one.",
            width=15,
            font=ctk.CTkFont(family="Constantia", size=15),
            wraplength=340,
        )
        self.api_label.grid(row=0, column=0, pady=(20, 0), padx=40, sticky="new")

        self.manager_tabview = ctk.CTkTabview(self.top)
        self.manager_tabview.segmented_button.configure(
            font=ctk.CTkFont(family="Constantia", size=12)
        )
        self.manager_tabview.grid(
            row=1, column=0, columnspan=2, padx=20, pady=(5, 20), sticky="nsew"
        )

        btn1_name, btn2_name = "ADD API KEY", "LOAD API KEY"
        self.manager_tabview.add(btn1_name)
        self.manager_tabview.add(btn2_name)
        self.manager_tabview.set(btn2_name)

        self.tabview_addbtn = ctk.CTkFrame(self.manager_tabview.tab(btn1_name))
        self.manager_tabview.tab(btn1_name).grid_columnconfigure(0, weight=1)

        self.tabview_loadbtn = ctk.CTkFrame(self.manager_tabview.tab(btn2_name))
        self.manager_tabview.tab(btn2_name).grid_columnconfigure(0, weight=1)

        self.add_tabview_frame()
        self.load_tabview_frame()

    def open_api_manager(self):
        self.top = ctk.CTkToplevel(self)
        self.top.withdraw()
        self.configure_api_manager_widgets()
        self.top.update_idletasks()
        self.top.after(10, lambda: self.top.deiconify())
        self.top.attributes("-topmost", True)

    def get_location(self):
        return self.text_field.get().strip()

    def update_app(self):
        location = self.get_location()
        self.button.configure(state="disabled")
        self.progress_bar.configure(mode="indeterminate", progress_color="yellow")
        self.progress_bar.start()

        def analyze_and_plot_thread():
            figure, data, buffer = analyze_and_plot(
                api_key=WeatherApp.current_user["api_key"],
                location=location,
                days=14,
                size=(7, 5),
            )

            if figure is not None and data is not None and buffer is not None:
                self.update_ui_with_data(data, figure)
                buffer.close()
                self.progress_bar.configure(
                    mode="determinate", progress_color=("green3", "chartreuse1")
                )

            elif data is not None and "error" in data:
                self.update_ui_with_error(data)
                self.progress_bar.configure(mode="determinate", progress_color="red")
            else:
                self.update_ui_with_error(
                    {"error": {"code": 503, "message": "No internet connection."}}
                )
                self.progress_bar.configure(mode="determinate", progress_color="red")

            self.progress_bar.stop()
            self.progress_bar.set(1)
            self.button.configure(state="normal")
            self.button.configure(state="enabled")

        # Start a new thread for the time-consuming task
        thread = threading.Thread(target=analyze_and_plot_thread)
        thread.start()

    def update_ui_with_data(self, data, figure):
        plotted_image = ctk.CTkImage(
            dark_image=figure, light_image=figure, size=(500, 360)
        )
        self.rounded_frame.configure(image=plotted_image, fg_color="white")
        self.update_text_box(self.bottom_box, self.format_info(data))
        self.update_text_box(
            self.weather_box,
            f"{data['current']['temp_c']}°C, {data['current']['condition']['text']}",
        )

    def update_ui_with_error(self, data):
        error_message = (
            f"code: {data['error']['code']}\nmessage: {data['error']['message']}"
        )
        self.update_text_box(self.bottom_box, error_message)

    @staticmethod
    def update_text_box(text_box, text):
        text_box.configure(state="normal")
        text_box.delete("0.0", "end")
        text_box.insert("0.0", text)
        text_box.configure(state="disabled")

    @staticmethod
    def format_info(data):
        return f"""- Location: {data['location']['name']}, \n\t{data['location']['region']}, {data['location']['country']}\n- Temperature: {data['current']['temp_c']}°C and {data['current']['temp_f']}°F\n- Feels Like: {data['current']['feelslike_c']}°C and {data['current']['feelslike_f']}°F\n- Condition: {data['current']['condition']['text']}\n- Atmospheric pressure: \n\t{data['current']['pressure_mb']} (mb), {data['current']['pressure_in']} (inHg)\n- Wind Speed: {data['current']['wind_kph']} km/h\n- Humidity: {data['current']['humidity']}%\n- Sunrise at {data['forecast']['forecastday'][0]['astro']['sunrise']} and \n\tSunset at {data['forecast']['forecastday'][0]['astro']['sunset']}\n- Moonrise at {data['forecast']['forecastday'][0]['astro']['moonrise']} and \n\tMoonset at {data['forecast']['forecastday'][0]['astro']['moonset']}\n- Moon Phase: {data['forecast']['forecastday'][0]['astro']['moon_phase']}
        """


if __name__ == "__main__":
    create_weather_api_table()
    app = WeatherApp(title="Weather Data Analysis", previous_data=load_from_json())
    app.iconbitmap(WeatherApp.resource_path(r"assets\sun.ico"))
    app.mainloop()
