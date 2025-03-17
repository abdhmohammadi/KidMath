
import random
import sys,os
from PySide6.QtGui import QPixmap,QIcon,QAction
from PySide6.QtCore import Qt,QSize,QTimer
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,QSizePolicy,
                               QLabel,QGridLayout, QHBoxLayout,QVBoxLayout,QRadioButton,
                               QMenuBar,QMessageBox)

class Game:

    def __init__(self, window:QMainWindow):
        self.window = window
        self.initValues()
    #        امتیازهای مراحل:اگر مقدار امتیازها را تغییر دادید این توضیحات
    #     رااصلاح کنید.امتیاز مراحل از یک الگوی عددی درست شئه است به طوریکه
    #                    است(i+1)x25 مجموع امتیازها حداکثر برابر i در مرحله 
    #                                               مرحله 1: حداکثر 50 امتیاز
    # مرحله 2: حداکثر 100 امتیاز(عدد 150 مربوط به جمع امتیاز دو مرحله است)
    # مرحله 3: حداکثر 150 امتیاز(عدد 300 مربوط به جمع امتیاز سه مرحله است)    
    def get_level_sum(self, level:int): return 25*(level+1)
    
    def get_avilable_levels(self):
        # خط زیر تعداد پوشه های موجود در مسیر را می شمارد
        # اگر تصاویر در پوشه ها کامل باشد بدون دستکاری کد 
        # میتوان تعداد مراحل ار افزایش داد
        available_levels = len([f for f in os.listdir('./assets') if f.startswith('level-')])
        return available_levels
    
    # مقدار دهی اولیه    
    def initValues(self):
        # جمع امتیازهای کودک
        self.kid_score = 0
        # تعداد غلط های کودک در پاسخ دادن به یک سوال                              
        self.kid_false_level = 0
        # تعداد ستاره های زرد: تعداد کل اشتباهات مجاز کودک در هنگام پاسخ به یک سوال
        self.kid_false_allowed_level = 3
        # تعداد غلط های کودک در پاسخ دادن به همه سوالها   
        self.kid_false_all = 0
        # تعداد قلب های قرمز: تعداد کل اشتباهات مجاز کودک در بازی
        self.kid_false_allowed = 10
        # شمارنده‌ی زمان بازی کامپیوتر در هر سوال
        self.ticks = 0
        # کل زمانی که در یک سوال به کامپیوتر اجازه داده می شود
        self.max_ticks = 2
        # معادله ای که در یک سوال استفاده می شود: مثلا اگر روی صفحه کارت 5 منهای کارت 3 دیده شود
        # این متغیر دارای مقدار "3 - 5" است
        self.equation = ''
        # مقادیر گزینه ها در هر سوال
        self.options = [] 
        # جواب معادله
        self.answer = -1   
        # شماره‌ی گزینه برای جواب
        self.answer_index = -1
        # نام بازیکن
        self.player = 'PC'
        # مجموع امتیاز کامپیوتر
        self.pc_score = 0
        # مقدار امتیاز در هر پاسخ درست 
        self.score_step = 10
        # شماره مرحله
        self.level = 1
        # تعداد مراحل ایجاد شده و قابل دسترس
        self.all_levels = self.get_avilable_levels()
        # عرض کارت برای نمایش
        self.card_width  = 150
        # ارتفاع کارت برای نمایش
        self.card_height = 200
        # سختی بازی: این گزینه ها فقط برای بازی کامپیوتر است:
        # آسان: کامپیوتر با احتمال 25% (1 به 4) جواب درست را حدس می زند
        # یعنی 1 جواب درست در بین 4 گزینه برای کامپیوتر قرار داده شده است
        # که شانسی یکی را انتخاب می  کند
        # #########################################################################
        # عادی: کامپیوتر با احتمال 50% (2 به 4) جواب درست را حدس می زند
        # یعنی 2 جواب درست در بین 4 گزینه برای کامپیوتر قرار داده شدهاست
        # که شانسی یکی را انتخاب می کند
        # ######################################################################## 
        # سخت: کامپیوتر با احتمال 75% (3 به 4) جواب درست را حدس می زند
        # یعنی 3 جواب درست در بین 4 گزینه برای کامپیوتر قرار داده شدهاست
        # که شانسی یکی را انتخاب می کند 
        self.difficulty_levels = ['Easy', 'Normal', 'Hard']
        # حالت انتخاب شده ی بازی
        self.difficulty = 'Easy'
        # اندازه عرض پنل چپ و راست بازیکنان
        self.pane_width = 280


    # آماده سازی شروع بازی و ساخت صفحه اول
    def Play(self):

        self.timer = QTimer(self.window)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_ticks)  
        self.window.setFixedHeight(700)
        self.window.setFixedWidth(1200)
        # layout with 3 column
        # left  :column Kid panel
        # right : column PC panel
        # center: game content
        self.grid_layout = QGridLayout()
        central_widget = QWidget()
        central_widget.setStyleSheet('background-color: blue')
        central_widget.setLayout(self.grid_layout)
        self.window.setCentralWidget(central_widget)
        # Init Kid panel
        kid_label = QLabel('کودک')
        kid_label.setStyleSheet('font-weight:bold;font: 24pt "Yas";text-align:center; background-color:olive;padding:5px')
        
        self.heart_label = QLabel()
        self.heart_label.setStyleSheet('color:RED;font: 14pt "Segoe Fluent Icons"')
        self.print_heart(self.kid_false_allowed)

        self.star_label = QLabel()
        self.star_label.setStyleSheet('color:YELLOW;font: 24pt "Segoe Fluent Icons"')
        self.print_star(self.kid_false_allowed_level)

        self.kid_score_label = QLabel('امتیاز: ' + str(self.kid_score))
        self.kid_score_label.setStyleSheet('font-weight:bold;font: 24pt "Yas"')

        # KID panel
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(10,20,10,20)
        
        left_layout.addWidget(kid_label)
        left_layout.addWidget(self.heart_label)
        left_layout.addWidget(self.star_label)
        left_layout.addWidget(self.kid_score_label)
        left_layout.addStretch(1)
        logo = QPixmap('./assets/logo.png')
        logo = logo.scaled(QSize(72,72))
        logo_label = QLabel()
        logo_label.setPixmap(logo)
        left_layout.addWidget(logo_label)
        left_layout.addWidget(QLabel('KidMath 1.0'))
        left_layout.addWidget(QLabel('AmirMohammad Mohammadi'))
        left_layout.addWidget(QLabel('Grade-7'))
        left_layout.addWidget(QLabel('1403(2025)'))
        left_widget = QWidget()
        left_widget.setFixedWidth(self.pane_width)
        left_widget.setStyleSheet('background-color: darkblue')
        left_widget.setLayout(left_layout)

        self.grid_layout.addWidget(left_widget,0,0,10,1)

        # Init PC panel
        pc_label = QLabel('رایانه')
        pc_label.setStyleSheet('font-weight:bold;font: 24pt "Yas";text-align:center; background-color:red;padding:5px')

        self.pc_score_label = QLabel('امتیاز: ' + str(self.pc_score))
        self.pc_score_label.setStyleSheet('font-weight:bold;font: 24pt "Yas"')
        
        self.timer_label = QLabel('')
        self.timer_label.setStyleSheet('font-weight:bold;font: 40pt "Yas";margin:0px;padding:0px')
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pc_answer_label = QLabel('آخرین نتیجه')
        self.pc_answer_label.setStyleSheet('font-weight:bold;font: 30pt "Yas";margin:0px;padding:0px')
        self.last_try = QLabel('')
        self.last_try.setStyleSheet('font-weight:bold;font: 24pt "Yas";margin:0px;padding:0px')
        self.last_try_result = QLabel('')
        self.last_try_result.setStyleSheet('font-weight:bold;font: 24pt "Yas";margin:0px;padding:0px')
        vlayout = QVBoxLayout()
        # Create radio buttons
        easy_button = QRadioButton('ضعیف')
        easy_button.setStyleSheet('font-weight:bold;font: 16pt "Yas";')
        easy_button.setChecked(True)
        normal_button = QRadioButton('عادی')
        normal_button.setStyleSheet('font-weight:bold;font: 16pt "Yas";')
        hard_button = QRadioButton('قوی')
        hard_button.setStyleSheet('font-weight:bold;font: 16pt "Yas";')
        
        # Add radio buttons to the layout
        vlayout.addWidget(easy_button)
        vlayout.addWidget(normal_button)
        vlayout.addWidget(hard_button)

        # Connect the radio buttons to the click event
        easy_button.clicked.connect(lambda: self.on_radio_button_clicked('Easy'))
        normal_button.clicked.connect(lambda: self.on_radio_button_clicked('Normal'))
        hard_button.clicked.connect(lambda : self.on_radio_button_clicked('Hard'))
        radio_widget = QWidget()
        radio_widget.setLayout(vlayout)

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10,20,10,20)
        right_layout.addWidget(pc_label)
        right_layout.addWidget(self.pc_score_label)
        right_layout.addWidget(self.timer_label)
        right_layout.addWidget(self.pc_answer_label)
        right_layout.addWidget(self.last_try)
        right_layout.addWidget(self.last_try_result)
        right_layout.addWidget(radio_widget)
        right_layout.addStretch(1)


        right_widget = QWidget()
        right_widget.setFixedWidth(self.pane_width)
        right_widget.setStyleSheet('background-color: darkblue')
        right_widget.setLayout(right_layout)
    
        self.grid_layout.addWidget(right_widget,0,2,10,1)#,Qt.AlignmentFlag.AlignTop)
        self.current_player_label = QLabel('کودک' if self.player == 'KID' else 'رایانه')
        
        # Set stretch factors for the row and column
        
        color = 'olive' if self.player == 'KID' else 'red'
        self.current_player_label.setStyleSheet(f'font-weight:bold;font:40pt "Yas";background-color:{color};')
        self.current_player_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center-align the text
        # Set the QLabel's size policy to expand
        #self.current_player_label.setSizePolicy(QSizePolicy.Policy.Minimum,  # Horizontal policy
        #                                        QSizePolicy.Policy.Ignored  # Vertical policy
        #                                        ) 
        #self.grid_layout.setRowStretch(0, 1)  # Row 0 will stretch
        self.grid_layout.setColumnStretch(1, 1)  # Column 0 will stretch
        self.grid_layout.addWidget(self.current_player_label,0,1,1,1)
        
        
        self.current_level_label = QLabel('مرحله: ' + str(self.level))
        self.current_level_label.setStyleSheet('font-weight:bold;font:30pt "Yas"; color:YELLOW')
        self.grid_layout.addWidget(self.current_level_label,3,0,1,3,Qt.AlignmentFlag.AlignCenter)

        self.play_btn = QPushButton(text='شروع بازی')

        self.play_btn.setStyleSheet('font-weight:bold;font: 40pt "Yas";margin:100px;padding:20px')
        self.play_btn.clicked.connect(self.play_clicked)
        self.grid_layout.addWidget(self.play_btn,0,1,4,1,Qt.AlignmentFlag.AlignVCenter)

        self.game_over_label = QLabel('بازی را باختید')
        self.game_over_label.setStyleSheet('font-weight:bold;font:40pt "Yas"; color: RED')
        self.grid_layout.addWidget(self.game_over_label,1,1,1,1,Qt.AlignmentFlag.AlignCenter)
        
        self.disable_interactions(True)

        self.game_over_label.hide()


        self.window.show()



    # وقتی کودک یک گزینه را انتخاب می کند این تابع اجرا می شود
    def kid_clicked(self,index):
        #                                      گزینه ای که کودک روی آن کلیک کرده است: index
        #                                    گزینه ی جواب درست در بین 4 گزینه: answer_index
        #       به این معنی است که کودک جواب درست را انتخاب کرده است answer_index == index
        #        در اینجا ما حالت نادرست باشد را کنترل می کنیم پس اگر این شرط نادرست باشد 
        # کودک یکی از گزینه های اشتباه را کلیک کرده است. پس اجرای برنامه وارد شرط می شود
        if not index == self.answer_index:
            #      چون کودک گزینه اشتباه را زده است، به اشتباهات او یک واحد افزوده می شود
            #                        اگر این اشتباهات به ده تا برسد کودک بازی را باخته است
            self.kid_false_all+= 1
            # این دستور تعداد قلب‌های باقیمانده را در زیر نام کودک در صفحه نمایش چاپ می‌کند
            self.print_heart(self.kid_false_allowed - self.kid_false_all)
            # در اینجا تعداد اشتباهات کودک فقط در سوالی که در حال جواب دادن آن است شمرده
            #  می‌شود، اگر کودک به یک سوال 3 جواب اشتباه بدهد بازی به کامپیوتر داده می‌شود
            self.kid_false_level += 1
            # این دستور تعداد ستاره‌ها را در زیر نام کودک در صفحه نمایش چاپ می‌کند، هر جواب
            #                                                     نادرست، یک ستاره کم می کند
            self.print_star(self.kid_false_allowed_level - self.kid_false_level)
            # در این جا تعداد اشتباهات کنترل می شود. اگر مجموع اشتباهات بیش از حد مجاز باشد
            # مشخص شده است kid_false_allowed بازی را باخته است، تعداد اشتباهات مجاز در متغیر 
            # به صور پیش فرض این مقدار را 10 قرار داده ایم، یعنی ده اشتباه مجاز در کل بازی
            if self.kid_false_allowed <= self.kid_false_all:
                # Game over
                # پیام پایان بازی نشان داده می شود و صفحه قفل می گردد 
                self.game_over_label.show()
                # اعلام پایان بازی به کودک
                self.current_player_label.setText('شما بیشتر از حد مجاز اشتباه کردید.')
                self.grid_layout.addWidget(self.current_player_label,4,0,2,3,Qt.AlignmentFlag.AlignCenter)
                    
                # این دستور صفحه را کاملا قفل می کند
                self.disable_interactions(False)
                # خارج می شود kid_clicked اجرای برنامه از تابع
                return
            #      در این جا تعداد اشتباهات سوال کنترل می شود. اگر مجموع اشتباهات بیش از حد مجاز باشد
            #  مشخص kid_false_allowed_level بازی به کامپیوتر داده می شود، تعداد اشتباهات مجاز در متغیر 
            # شده است به صور پیش فرض این مقدار را 3 قرار داده ایم، یعنی 3 اشتباه مجاز در هر سوال بازی            
            if self.kid_false_allowed_level <= self.kid_false_level:
                # تنظیم بازی برای نوبت کامپیوتر
                self.load_game('PC')

        else:#        وقتی کودک جواب درست را بدهد این قسمت اجرا می شود  
            #       افزایش داده می شود score_step امتیاز کودک به اندازه 
            # این متغیر امتیاز هر جواب درست را مشخص می کند: score_step
            #           به طور پیش فرض مقدار آن را 10 در نظر گرفته ایم
            #                          یعنی هر جواب درست ده امتیاز دارد
            self.kid_score += self.score_step
            # دستور زیر امتیاز کودک را در صفحه نمایش زیر نام کودک بروز رسانی می کند
            self.kid_score_label.setText('امتیاز: '+ str(self.kid_score))
            # اگر مجموع امتیازات کسب شده از مجموع امتیازات تا مرحله جاری بیشتر باشد
            #       محاسبه می شود get_level_sum مجموع امتیازات تا هر مرحله توسط تابع 
            if self.kid_score >= self.get_level_sum(self.level):
                # مرحله بالاتر می رود
                self.level += 1
                # در صفحه نمایش و درر وسط صفحه زیر کزینه ها، مرحله بازی چاپ می شود
                self.current_level_label.setText('مرحله: ' + str(self.level))
                # بازی در حال حاضر حداکثر 3ه مرحله دارد، اگر شماره مرحله از 3 بگذرد
                #                                              به معنای پایان بازی است
                if self.level >self.all_levels:
                    # اعلام پایان بازی به کودک
                    self.current_player_label.setText('آفرین بر شما! همه مراحل را پشت سرگذاشتید')
                    self.grid_layout.addWidget(self.current_player_label,4,0,10,10,Qt.AlignmentFlag.AlignCenter)
                    self.current_level_label.hide()
                    # صفحه نمایش قفل می شود
                    self.disable_interactions(False)

                    return
            # بازی به کامپیوتر منتقل می شود
            self.load_game('PC')



    # این متد(تابع) به تعداد عدد داده شده قلب قرمز رنگ در زیر اسم کودک چاپ می کند
    def print_heart(self,n:int):
        # تعداد قلب هایی که باید چاپ شود: n        
        #این متغیر خالی است و داخل حلقه زیر کارکترهای قلب در آن قرار می گیرد
        text=''
        # کد کاراکتر قلب در سیستم یونیکد برابر این مقدار است: E00B
        # این حلقه به تعداد عدد داده شده به تابع می چرخد و به همان
        #       قرار می دهد text تعداد قلب تولید می کند و در متغیر
        for i in range(n):  text = text + ' \uE00B'
        # قلب ها را  چاپ میکند
        self.heart_label.setText(text)



    # چاپ ستاره ها
    def print_star(self,n:int):
        # تعداد ستاره هایی که باید چاپ شود: n
        #این متغیر خالی است و داخل حلقه زیر کارکترهای ستاره در آن قرار می گیرد
        text=''
        #     کد کاراکتر ستاره در سیستم یونیکد برابر این مقدار است: E00A
        # این حلقه به تعداد عدد داده شده به تابع می چرخد و به همان تعداد
        #                  قرار می دهد text ستاره تولید می کند و در متغیر
        for i in range(n): text = text + '\uE00A'
        # ستاره ها را  چاپ میکند
        self.star_label.setText(text)



    # کارتی را از مسیر معرفی شده می خواند و به برنامه منتقل می کند
    def upload_card(self,path):
        # آدرس فایل تصویر: path
        # آیا این متغیر دارای مقدار است
        if path:
            # تعیین اندازه تصویر
            size = QSize(self.card_width, self.card_height)
            # خواندن تصویر از  فایل داده شده
            pixmap = QPixmap(path)
            # Scale the photo to fill the entire photo box (ignore aspect ratio)
            # تصویر به مقدار اندازه تعیین شده کوچک می شود
            return pixmap.scaled(size, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)

        # اگر متغیر آدرس خالی باشد
        return None


    # این تابع سه گزینه تصادفی از پوشه جوابها انتخاب می کند
    #                 و جواب اصلی را در بین آنها قرار می دهد
    def generate_options(self):

        # تعیین مسیر جوابها در مرحله‌ی جاری
        #شناسایی مسیرها توسط برنامه: ساختار فایل های برنامه در فایل متنی همراه برنامه
        # قرار دارد طبق این ساختار، برنامه می تواند با استفاده از شماره مرحله به همه‌ی
        # به صورت زیر است i تصاویر دسترسی داشته باشد، قالب دسترسی به فایل ها در مرحله 
        # ./assets/level-i/answers/ کارتهای جواب
        # ./assets/level-i/cards/   کارتهای سوال 
        # ./assets/signs/   کارتهای عملگر ریاضی
        option_path = './assets/level-' + str(self.level)+'/answers'
        # خط زیر نام تمام فایل های موجود در مسیر مرحله را در لیست قرار می دهد
        cards = [f.split('.')[0] for f in os.listdir(option_path) if f.endswith('.png')]
        #  چون جواب هر سوال از قبل مشخص است، ابتدا جواب از بین انتخاب ها حذف می شود
        #  سپس سه گزینه از بین لیست جوابها انتخاب می شود و در آخر گزینه جواب در بین
        #  گزینه‌ها قرار داده می‌شود به این ترتیب از گزینه تکراری و محاسبه نادرست نیز
        #                                                                جلوگیری می شود
        cards.remove(str(self.answer))
        # انتخاب 3 گزینه
        self.options = random.sample(cards,3)
        #          انتخاب تصادفی محل گزینه برای جواب در بین 4 گزینه
        # چون گزینه ها از صفر تا سه شماره گذاری شده منهای یک کردیم
        self.answer_index = random.choice([1,2,3,4])-1
        # افزودن جواب در بین گزینه های دیگر و در محل انتخاب شده در خط قبل
        self.options.insert(self.answer_index,str(self.answer))


    # کارت 1، کارت 2 و عملگر برگشت داده می شود
    def choose_question(self):
        #  با توجه به مرحله بازی دو کارت از پوشه کارت ها انتخاب می شود
        # خط زیر مسیر انتخاب کارتها را از طریق شماره مرحله مشخص می کند
        card_path = './assets/level-' + str(self.level)+'/cards'
        # لیست کارتهای موجود در مسیر مشخص شده را دریافت می کند
        cards = [f.split('.')[0] for f in os.listdir(card_path) if f.endswith('.png')]

        #   دو نمونه تصادفی از کارتها را انتخاب می کند، هر انتخاب مشخص کننده ی
        # مسیر یک کارت است، بنابراین با استفاده از این مقادیر به تصاویر دسترسی
        #                                                             پیدا می کنیم
        choises = random.sample(cards,2)
        card1 = int(choises[0])
        card2 = int(choises[1])
        # حالا باید عملگر ریاضی را مشخص کنیم
        sign_path = './assets/signs'
        # مانند انتخاب کارت، در اینجا نیز به طور تصادفی یکی از عملگرها انتخاب می شود
        signs = [f.split('.')[0] for f in os.listdir(sign_path) if f.endswith('.png')]

        # است minus یا plus مقدار این متغیر به صورت
        operator = random.sample(signs,1)[0]

        #    بعضی  مواقع ممکن است کارت اول از کارت دوم کوچکتر باشد
        #    در این صورت اگر عملگر منها انتخاب شده باشد کودک دوره‌ی
        # ابتدایی نمی تواند محاسبه علامت دار انجام دهد به همین دلیل
        # جای دو کارت را تعویض می کنیم تا مطمئن شویم جواب مثبت است
        if operator == 'minus' and card1< card2:
            tmp   = card1
            card1 = card2
            card2 = tmp

        # با توجه به علامت انتخاب شده محاسبه انجام می شود و نتیجه ذخیره می گردد
        self.answer = card1 - card2 if operator =='minus' else card1 + card2
        # از عبارت زیر فقط برای نشان دادن بازی آخر کامپیووتر در صفحه نمایش استفاده می کنیم
        self.equation = str(card1) + str('+' if operator == 'plus' else '-') + str(card2) + ' = '
        # کارت 1، کارت 2 و عملگر برگشت داده می شود
        return card1, card2, operator 


    # تعیین سطح بازی کامپیوتر
    def pc_chances(self):
        #                                                 تعیین قدرت بازی کامپیوتر
        #     به طور پیش فرض کامیپوتر با احتمال یک چهارم(25%) جواب را حدس می زند
        # این کار با انتخاب تصوادفی شماره گزینه از بین اعداد 0 تا 3 انجام می شود
        chances = [0,1,2,3]
        # اگر حالت متوسط انتخاب شود در بین 4 گزینه 2 گزینه درست قرار می‌دهیم مثلا
        #  اگر گزینه درست گزینه 3 باشد یک لیست به شکل [0,3,1,3] برای انتخاب جواب
        #                   تولید می شود بنابراین شانس انتخاب عدد 3 بالاتر می رود
        if self.difficulty == self.difficulty_levels[1]: 
            # Normal: PC guesses the answer with a 50% probability.
            # برای جلوگیری از انتخاب تکراری، گزینه جواب از لیست حذف می شود
            chances.remove(self.answer_index)
            # دو گزینه از سه گزینه ی باقیمانده انتخاب می شود
            chances = random.sample(chances,2)
            # دوبار گزینه جواب به لیست گزینه ها افزوده می شود
            chances.append(self.answer_index)
            chances.append(self.answer_index)
            # نتیجه مجددا به هم ریخته می شود
            random.shuffle(chances)
            # یک لیست چهار گزسنه ای که دو تا  عدد با گزینه درست در آن قرار دارد
            #                                                     برگردانده می شود
            #return chances

        # اگر حالت قوی انتخاب شود در بین 4 گزینه 3 گزینه درست قرار می دهیم مثلا
        #   اگر گزینه درست گزینه 3 باشد یک لیست به شکل [3,3,2,3] برای انتخاب جواب
        #                        تولید می شود بنابراین شانس انتخاب عدد 75% می شود
        elif self.difficulty == self.difficulty_levels[2]: 
            # Hard: PC guesses the answer with a 75% probability.
            # برای جلوگیری از انتخاب تکراری، گزینه جواب از لیست حذف می شود
            chances.remove(self.answer_index)
            # فقط یک گزینه از سه گزینه ی باقیمانده انتخاب می شود
            chances = random.sample(chances,1)
            # سه بار گزینه جواب به لیست گزینه ها افزوده می شود
            chances.append(self.answer_index)
            chances.append(self.answer_index)
            chances.append(self.answer_index)
            # نتیجه مجددا به هم ریخته می شود
            random.shuffle(chances)
            # یک لیست چهار گزسنه ای که سه تا عدد با گزینه درست در آن قرار دارد
            #                                                    برگردانده می شود
        
        return chances
 
    
    
    # بارگزاری تصاویر بازی و آماده سازی
    def load_game(self,player):
        # ذخیره بازیکن
        self.player = player
        # چاپ نام بازیکن جاری در وسط صفحه
        self.current_player_label.setText('کودک' if 'KID'== self.player else 'رایانه')
        # تعیین رنگ زمینه بازیکن
        color = 'olive' if self.player == 'KID' else 'red'
        self.current_player_label.setStyleSheet(f'font-weight:bold;font:40pt "Yas";background-color:{color};border-radius:8px')
        # که در جای خود توضیح داده شده است در اینجا فراخوانی میشود self.choose_question تابع 
        #           که یک سوال جدید می سازد و عدد اول، عدد دوم و عملگر ریاضی را برمی گرداند
        card1, card2, operator = self.choose_question()
        # این تابع نیز 4 گزینه برای جوابها را تولید می کند
        self.generate_options()
        # خطوط پایین براساس کراتهای بدست آمده تصاویر را از مسیرهای مخصوص خوانده
        #      و وارد صفحه نمایش می کنند، مسیرها براساس شماره مرحله تعیین می شود
        card1_path = './assets/level-' + str(self.level)+'/cards/' + str(card1) + '.png'
        card2_path = './assets/level-' + str(self.level)+'/cards/' + str(card2) + '.png'
        sign__path = './assets/signs/'+operator+'.png'
        card1_img = self.upload_card(card1_path)
        card2_img = self.upload_card(card2_path)
        sign__img = self.upload_card(sign__path)
        card1_lbl = QLabel()
        card1_lbl.setPixmap(card1_img)
        card2_lbl = QLabel()
        card2_lbl.setPixmap(card2_img)
        sign__lbl = QLabel()
        sign__lbl.setPixmap(sign__img)
    
        equation_layout = QHBoxLayout()
        equation_layout.addStretch()
        equation_layout.addWidget(card1_lbl)
        equation_layout.addWidget(sign__lbl)
        equation_layout.addWidget(card2_lbl)
        equation_layout.addStretch()
        equation_widget = QWidget()
        equation_widget.setStyleSheet('background-color:GREEN; border-radius:8px')
        equation_widget.setLayout(equation_layout)

        self.grid_layout.addWidget(equation_widget,1,1,Qt.AlignmentFlag.AlignTop)

        option_layout = QHBoxLayout()
        # چهار کارت بارگیری می شود
        for i in range(4):

            card_path = './assets/level-'+str(self.level)+'/answers/'+self.options[i]+'.png'
            image = self.upload_card(card_path)
            icon = QIcon(image)
            lbl = QPushButton("",self.window)
            # Optionally, set the icon size
            lbl.setIconSize(QSize(image.size().width()-10,image.size().height()-10)) 
            lbl.setContentsMargins(5,5,5,5)
            lbl.setFixedSize(image.size())
            # Set the button size policy to expand
            lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            # Optional: Set a stylesheet to ensure hover effects work
            lbl.setStyleSheet("""
            QPushButton 
            {
                border: 2px solid #8f8f91;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover 
            {
                background-color:yellow;
            }
            """)
            # Set the icon on the QPushButton
            lbl.setIcon(icon)
            #lbl = ClickableLabel()
            #lbl.setPixmap(image)
            if player == 'KID':
                lbl.clicked.connect(lambda _,index=i: self.kid_clicked(index=index))
            
            option_layout.addWidget(lbl)
    
        # پس از بارگیری تصاویر گزینه ها، تصاویر به صفحه نمایش منتقل می شود
        option_widget = QWidget()
        option_widget.setLayout(option_layout)
        self.grid_layout.setAlignment(option_widget, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        option_widget.setStyleSheet('background-color:GREEN; border-radius:8px')
        self.grid_layout.addWidget(option_widget,2,1,Qt.AlignmentFlag.AlignTop)
        
        # اگر نوبت بازی کامپیوتر باشد شمارنده زمان فعال می شود
        if self.player == 'PC':
            self.ticks = 0
            # پس از این دستور، شمارنده فعال می شود
            self.timer.start() 

        else : self.kid_false_level = 0 

   
    
    # کنترل بازی کامپیوتر
    def update_ticks(self):
        # وقتی بازی به کامپیوتر داده می شود هر یک ثانیه 1 بار این کد فراخوانی می شود
        #                                         وظیفه آن شمردن زمان بازی کامپیوتر است
        self.ticks += 1
        # زمان محاسبه شده را در صفحه در بخش اطلاعات بازی نشان می دهد
        self.timer_label.setText(str(self.ticks))
        # اگر هنوز زمان باقی مانده باشد وارد شرط می شود 
        if self.ticks > self.max_ticks:
            # شمارنده زمان متوقف می شود
            self.timer.stop()
            #  مقدار شمارنده صفر می شود
            self.ticks = 0
            #                                     فراخوانی می شود self.pc_chances() تابع
            # بر اساس توضیحاتی که در تابع داده شد در اینجا شانس کامپیوتر تعیین می شود
            #               و براساس آن شانس کامپیوتر یک گزینه را تصادفی انتخاب می کند
            pc_option = random.choice(self.pc_chances())
            #           اگر گزینه انتخابی کامپیوتر برابر گزینه جواب باشد وارد شرط می شود
            # درون شرط امتیاز این مرحله حساب می شود ولی اگر وارد شرط نشود امتیاز نمیگیرد  
            if pc_option == self.answer_index:
                # افزودن امتیاز به اندازه مقدار تعیین شده
                # این مقدار بطور پیش فرض 10 تعیین شده است
                self.pc_score += self.score_step
                # نمایش امتیاز در بخش اطلاعات بازی
                self.pc_score_label.setText('امتیاز: ' + str(self.pc_score))
                # اگر امتیاز کامپیوتر کامل شده باشد آن را برنده اعلام می کند و بازی تمام می شود
                if self.pc_score >= self.get_level_sum(self.all_levels) :
                    self.current_player_label.setText('کامپیوتر بیشترین امتیاز را کسب کرد، شما بازی را باختید.')
                    self.disable_interactions(False)
                    return
            
            # نمایش آخرین نتیجه در بخش اطلاعات بازی 
            self.last_try.setText( self.equation + self.options[pc_option])
            # چاپ درستی یا ندرستی
            self.last_try_result.setText('درست' if pc_option == self.answer_index else 'نادرست')
                
            # دوباره زمان صفر نشان داده می شود
            self.timer_label.setText('00:00')
            # حالا بازی کودک شروع می شود. در هر شروع کودک تعداد اشتباهات مرحله صفر است
            self.kid_false_level = 0
            # ستاره ها چاپ می شود
            self.print_star(self.kid_false_allowed_level)
            # سوالات جدید برای کودک نشان داده می شود                
            self.load_game('KID') # Load for Kid        


    # وقتی شروع بازی کلیک شوداین قسمت فراخوانی می شود
    def play_clicked(self):
        # دستور شروع مخفی می شود
        self.play_btn.hide()
        # سوالها نمایش داده می شود
        # توضیحات تابع در خود تابع نوشته شده است
        self.load_game('PC')



    # وقتی کاربر روی گزینه های سختی بازی کلیک می کند این قسمت
    #       فراخوانی می شود و میزان سختی بازی را تنظیم می کند
    def on_radio_button_clicked(self,arg): self.difficulty = arg
   


    # قفل کردن صفحه هنگام باخت یا پایان بازی
    def disable_interactions(self,allow:bool):
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setDisabled(not allow)


def play_new_game(parent):
    game = Game(parent)
    
    game.Play()

def show_about_me(parent):
    about ="سازنده: امیرمحمد محمدی\n" 
    about +="پایه هفتم/دبیرستان ایثار-بجنورد\n"
    about +="ارائه شده در یازدهمین جشنواره نوجوان خوارزمی\n\n"
    about +="شرح کوتاه:این بازی برای آموزش جمع و تفریق اعداد دو رقمی برای "
    about +="کودکان دوره اول ابتدایی طراحی شده است، بازی در ورژن 1 که برای "
    about +="ارائه در یازدهمین جشنواره نوجوان خوارزمی آماده شده است، دارای سه "
    about +="مرحله می باشد. جهت ارتقاء و افزایش مراحل بازی کافیست داده های "
    about +=" تصایر بازی را در مسیر مناسب قرار دهیم. برای تماس با ما می توانید "
    about +=" از روشهای زیر استفاده کنید\n\n"
    about +="امیرمحمد محمدی در برنامه شاد\n\n"
    about +="https://shad.ir/AmirMMohammadi1391\n\n"
    about +="تماس(والدین): 09372561238"
    QMessageBox.information(parent,'درباره ما',about)


if __name__ == "__main__":

    
    app = QApplication()

    app.setWindowIcon(QIcon('./assets/logo.png'))

    window = QMainWindow()
    window.setWindowTitle('KidMath v1.0')
    # Create a menu bar
    menu_bar = QMenuBar()
    window.setMenuBar(menu_bar)

    # Create a file menu
    file_menu = menu_bar.addMenu("بازی")

    # Create a new action
    new_action = QAction("بازی جدید",window)
    file_menu.addAction(new_action)
    new_action.triggered.connect(lambda _, arg=window: play_new_game(arg))

    # Create a new action
    about_action = QAction("درباره ما",window)
    file_menu.addAction(about_action)
    about_action.triggered.connect(lambda _,arg=window: show_about_me(arg))
    # Create an exit action
    exit_action = QAction("خروج", window)
    file_menu.addAction(exit_action)

    # Connect the exit action
    exit_action.triggered.connect(window.close)



    play_new_game(window)
    
    sys.exit(app.exec())