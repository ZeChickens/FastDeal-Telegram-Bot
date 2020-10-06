import pyodbc
from datetime import timedelta, date, datetime
import error_logging

class Data:
    def __init__(self, bot):
        self.REDACTION_CHAT_ID = -1001378510647
        self.bot = bot

        self.message = Message()
        self.dbo = Dbo(bot=bot)

    def get_channel(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_channel, values=col,
                                     where=where, sign=signs, order_by=order_by) 

        return rows

    def add_channel(self, link, name, subscribers=0, price=0,
                    photo="None", description="None", 
                    tag_id=None, statistic_id=None, owner_id=None, status=0,
                    register_date=date.today()):
        values = [link, name, subscribers, price, photo, description, statistic_id, tag_id, owner_id, status, register_date]

        self.dbo.add_value(self.dbo.table_channel, *values)

    def update_channel(self, set_=dict(), where=dict()):
        col = [[k] for k, v in set_.items()]
        value = [[v] for k, v in set_.items()]
        where, where_value = [[k, v] for k, v in where.items()][0]
        self.dbo.update_value(table=self.dbo.table_channel, column=col, value=value,
                              where=where, where_value=where_value)
    
    def get_channel_stats(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_channel_stats, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

    def add_channel_stats(self, one_post, one_post_last_day, er, er_last_day): 
        values = [one_post, one_post_last_day, er, er_last_day]

        self.dbo.add_value(self.dbo.table_channel_stats, *values)
        
    def update_channel_stats(self, set_=dict(), where=dict()):
        col = [[k] for k, v in set_.items()]
        value = [[v] for k, v in set_.items()]
        where, where_value = [[k, v] for k, v in where.items()][0]
        self.dbo.update_value(table=self.dbo.table_channel_stats, column=col, value=value,
                              where=where, where_value=where_value)

    def get_client(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_client, values=col,
                                     where=where, sign=signs, order_by=order_by) 

        return rows

    def add_client(self, chat_id, username, name, 
                   surname, register_date, last_interaction_time):
        values = [chat_id, username, name, surname, register_date, last_interaction_time]

        self.dbo.add_value(self.dbo.table_client, *values)

    def update_client(self, set_=dict(), where=dict()):
        col = [[k] for k, v in set_.items()]
        value = [[v] for k, v in set_.items()]
        where, where_value = [[k, v] for k, v in where.items()][0]
        self.dbo.update_value(table=self.dbo.table_client, column=col, value=value,
                              where=where, where_value=where_value)

    def get_order(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_order, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

    def add_order(self, client_id, channel_id, text, photo, 
                  comment, post_date, order_date, redaction_comment=None, 
                  status=0, owner_comment=None, post_statistic_id=None):
        values = [client_id, channel_id, text, photo, 
                  comment, post_date, order_date, redaction_comment, 
                  status, owner_comment, post_statistic_id]

        self.dbo.add_value(self.dbo.table_order, *values)
        
    def update_order(self, set_=dict(), where=dict()):
        col = [[k] for k, v in set_.items()]
        value = [[v] for k, v in set_.items()]
        where, where_value = [[k, v] for k, v in where.items()][0]
        self.dbo.update_value(table=self.dbo.table_order, column=col, value=value,
                              where=where, where_value=where_value)

    def get_post_statistic(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_post_statistic, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

    def add_post_statistic(self, post_id, post_link, post_text, views_count, 
                           post_time, channel_link=None, subscribers_on_start=None, 
                           subscribers_in_half_day=None, subscribers_in_day=None):
        values = [post_id, post_link, post_text, views_count, 
                  post_time, channel_link, subscribers_on_start, 
                  subscribers_in_half_day, subscribers_in_day]

        self.dbo.add_value(self.dbo.table_post_statistic, *values)
        
    def update_post_statistic(self, set_=dict(), where=dict()):
        col = [[k] for k, v in set_.items()]
        value = [[v] for k, v in set_.items()]
        where, where_value = [[k, v] for k, v in where.items()][0]
        self.dbo.update_value(table=self.dbo.table_post_statistic, column=col, value=value,
                              where=where, where_value=where_value)

    def get_payment(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_payment, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

    def add_payment(self, order_id, order_reference, reason, 
                    amount, currency, created_date, processing_date, 
                    card_pan, card_type, issuer_bank_country, 
                    issuer_bank_name, transaction_status, refund_amount,
                    fee, merchant_signature):
        values = [order_id, order_reference, reason, 
                  amount, currency, created_date, processing_date, 
                  card_pan, card_type, issuer_bank_country, 
                  issuer_bank_name, transaction_status, refund_amount,
                  fee, merchant_signature]

        self.dbo.add_value(self.dbo.table_payment, *values)

    def update_payment(self, set_=dict(), where=dict()):
        col = [[k] for k, v in set_.items()]
        value = [[v] for k, v in set_.items()]
        where, where_value = [[k, v] for k, v in where.items()][0]
        self.dbo.update_value(table=self.dbo.table_payment, column=col, value=value,
                              where=where, where_value=where_value)

    def get_order_status(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_order_status, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

    def get_channel_status(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_channel_status, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

    def get_owner(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_owner, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

    def add_owner(self, chat_id, nickname, name, 
                  surname, register_date, last_interaction_time):
        values = [chat_id, nickname, name, surname, 
                  register_date, last_interaction_time]

        self.dbo.add_value(self.dbo.table_owner, *values)
        
    def update_owner(self, set_=dict(), where=dict()):
        col = [[k] for k, v in set_.items()]
        value = [[v] for k, v in set_.items()]
        where, where_value = [[k, v] for k, v in where.items()][0]
        self.dbo.update_value(table=self.dbo.table_owner, column=col, value=value,
                              where=where, where_value=where_value)

    def get_tag(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_tag, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

    def get_multiple_tables(self, tables:list, join_type="Right", col=["*"], where=None, signs=["="], order_by=None):
        table_string = f"[{tables[0]}] "

        table_index = 0
        while table_index < len(tables)-1:
            table_name_1 = tables[table_index]
            table_name_2 = tables[table_index+1]

            table_string += (f"{join_type} "
                             f"JOIN [{table_name_2}] "
                             f"ON [{table_name_1}].{table_name_1}ID = [{table_name_2}].{table_name_1}ID "
            )

            table_index += 1
        rows = self.dbo.select_table(table=table_string, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

class Dbo:

    def __init__(self, bot):
        self.bot = bot
        self._init_table_names()
        self._connect_to_database()
    
    def _connect_to_database(self):
        #Computer DESKTOP-2IT0PLT
        #Laptop   DESKTOP-4T7IRV2
        print("Connecting to database...")
        try:
            self.connection = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                                        'Server=104.154.69.146;'
                                        'Database=FastDeal;'
                                        'uid=sqlserver;'
                                        'pwd=zeOrd@;')
            print("Database connected succesfully!")
        except:
            raise ConnectionError
                      
        self.cursor = self.connection.cursor() 

    def _init_table_names(self):
        self.table_channel = "Channel"
        self.table_channel_status = "Channel_Status"
        self.table_channel_stats = "Channel_Statistic"
        self.table_client = "Client"
        self.table_order = "Order"
        self.table_order_status = "Order_Status"
        self.table_payment = "Payment"
        self.table_post_statistic = "Post_Statistic"
        self.table_owner = "Owner"
        self.table_tag = "Tag"

    def select_table(self, table, values, sign, where=None, order_by=None):
        select_clause = str()

        # Values
        for value in values:
            if value != "*":
                select_clause += "[{}], ".format(value)
            else:
                select_clause += "{}, ".format(value)
        select_clause = select_clause[:-2]
        
        # Where clause
        where_clause = str()
        if where is not None:
            where_clause = "WHERE "
            index = 0
            for key, value in where.items():
                if not isinstance(value, int) and not isinstance(value, date):
                    value = "N'{}%'".format(value)
                    where_clause += "{} LIKE {} AND ".format(key, value)
                else:
                    if isinstance(value, datetime):
                        date_time = value.strftime("%Y-%m-%d %H:%M:%S")
                        value = f"'{date_time}', "
                    elif isinstance(value, date):
                        value = f"'{str(value)}'"
                    where_clause += "{} {} {} AND ".format(key, sign[index], value)
                index += 1
            where_clause = where_clause[:-4]

        # Order By clause
        order_by_clause = str()
        if order_by is not None:
            value, direction = [[k, v] for k, v in order_by.items()][0]
            order_by_clause = f"ORDER BY {value} {direction}"

        table = f"[{table}]" if "[" not in table else table
        query = """ SELECT {}
                    FROM {}
                    {}
                    {}""".format(select_clause, table, where_clause, order_by_clause)
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
        except:
            error_logging.send_error_info_message(bot=self.bot, current_frame=error_logging.currentframe(),
                                                  additional_info=query)
            return list()

        return rows

    def add_value(self, table, *values):
        value = str()
        for item in values:
            if item == None:
                value += "Null, "
            elif isinstance(item, datetime):
                date_time = item.strftime("%Y-%m-%d %H:%M:%S")
                value += f"'{date_time}', "
            elif isinstance(item, date):
                value += f"'{str(item)}', "
            elif isinstance(item, int) or isinstance(item, float):
                value += "{}, ".format(item)
            else:
                item = item.replace("'", "`")
                value += "N'{}', ".format(item)
        value = value[:-2] #erase , in the end

        query = """ INSERT INTO [{}]
                    VALUES ({})""".format(table, value)
        
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("{} added succesfully!".format(table))
        except:
            error_logging.send_error_info_message(bot=self.bot, current_frame=error_logging.currentframe(),
                                                  additional_info=query)
            print("New {} not added(((".format(table))

    def update_value(self, table, column, value, where, where_value):
        
        values = str()
        for col, val in zip(column, value):
            if val[0] == None:
                values += f"{col[0]} = Null, "
            elif  isinstance(val[0], datetime):
                date_time = val[0].strftime("%Y-%m-%d %H:%M:%S")
                values += f"{col[0]} = '{date_time}', "
            elif isinstance(val[0], date):
                values += f"{col[0]} = '{str(val[0])}', "
            elif not isinstance(val[0], int):
                values += f"{col[0]} = N'{val[0]}', "
            else:
                values += f"[{col[0]}] = {val[0]}, "
        values = values[:-2]

        if not isinstance(where_value, int):
            where_value = "N'{}'".format(where_value)
        
        query = """ UPDATE [{}]
                    SET {}
                    WHERE [{}] = {}""".format(table, values, where, where_value)

        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("{} {} updated succesfully!".format(table, column))
        except:
            error_logging.send_error_info_message(bot=self.bot, current_frame=error_logging.currentframe(),
                                                  additional_info=query)
            print("{} {} failed to update(((".format(table, column))

#TO DO
#transfer to sql later
class Message:
    def __init__(self):
        self._init_messages()

    def _init_messages(self):
        self.start_bot = (
            "Привіт!\n" 
            "Ну що ж, розпочнемо пошук ідеального каналу для вашої реклами.\n\n"
            "Я -  FastDeal Telegram, бот-біржа з замовлення реклами у Telegram, допоможу у цьому.\n\n"
            "Вірю, що я буду такою ж цінною для Вас, як для мене цей прекрасний месенджер.\n"
            "Тому успадкувала собі його ж простоту, швидкість та надійність.\n\n"
            "А тепер, ознайомлюйтеся та скоріш переходьте до вибору категорій."
        )

        self.tag_choose = (
            "Яка Ваша цільова аудиторія?\n"
            "🎯 Вибери свою категорію:"
        )
        self.tag_empty = "Поки що пусто("
        self.tag_first_page = "Схоже ти на самому початку!"
        self.tag_last_page = "Ой, це вже остання сторінка!"

        self.channel_choose = "Виберіть канал для детальнішої інформації:"
        self.channel_description_description = "🗒<i><u>Опис каналу</u></i>"
        self.channel_description_subs = "👥<i>Підписники</i>"
        self.channel_description_price = "💰<i>Ціна</i>"
        self.channel_description_post_views = "👁<i><u>Переглядів на пост</u></i>"
        self.channel_description_post_views_last_seven_days = "🔹<i>За останній тиждень</i>"
        self.channel_description_post_views_last_day = "🔸<i>За останні 24 години</i>"
        self.channel_description_er = "📈<i><u>ER</u></i> (процент підписників, яка взаємодіяла з постами)"
        self.channel_description_er_last_seven_days = "🔹<i>Тижневий</i>"
        self.channel_description_er_last_day = "🔸<i>Денний</i>"

        self.calendar_choose_date = "Виберіть потрібну дату"

        self.order_wait_photo = "Надішліть мені <b>фото</b> яке ви хочете бачити у вашій рекламі (якщо таке існує)"
        self.order_wait_text = (
            "Очікую <b>текст</b> вашої реклами.\n\n"
            "❗️ Щоб ваше замовлення було виконане, переконайтесь, що ви дотримались всіх правил вказаних вище"
        )
        self.order_wait_comment = (
            "Напишіть ваш <b>коментар</b> до замовлення.\n\n" 
            "<i>Тут ви можете вказати наступне:</i>\n"
            "🕔 Бажаний проміжок часу\n"
            "📝 Вказівки до оформлення вашої реклами (прикріпити кнопку та ін.)"
        )
        self.order_description_text = "<b>Текст</b>"
        self.order_description_client_comment = "<b>Коментар замовника</b>"
        self.order_description_redaction_comment = "<b>Коментар редакції</b>"
        self.order_description_status = "<b>Статус: </b>"
        self.order_status_notification = "У вашому замовленні відбулись зміни"
        self.order_status_redaction_rejected = "замовлення не пройшло перевірку редакції"
        self.order_canceled = "Замовлення успішно скасовано!"
        self.order_formed = (
            "🔅Готово!\n"
            "Ваше замовлення проходить перевірку редакції та власника.\n"
            "Очікуйте відповіді протягом 12 годин.\n\n"
            "У випадку відхилення, Ви отримаєте повернення коштів."
        )
        self.order_sent_to_redaction = "Готово!\nВаше замовлення надіслане на перевірку.\nОчікуйте рішення на протязі дня."
        self.order_list = "Список усіх замовлень:"
        self.order_payment_error = "Упс!\nСталась невідома мені помилка😐\nСпробуй ще раз"
        self.order_payment_confirmation_wait = "📩 Зачекайте декілька хвилин, ваша оплата обробляється."
        self.order_payment_time_is_up = (
            "❌ Ви не оплатили замовлення.\n\n"
            "Спробуйте замовити ще раз, або зверніться у підтримку /help."
        )
        self.order_payment_refund_wait = "Зачекайте, роблю всьо шо нада."
        self.order_payment_refund_completed = "Я всьо вернув клієнту!\nНадіюсь..."



        self.redaction_results_sent_to_client = "Результат надіслано клієнту!"
        self.redaction_new_order_notification = "Нове замовлення!"
        self.redaction_reject_reason = "Введіть причину відказу"
        self.redaction_reject_order = "Замовлення відхилено!\nДеталі надіслано клієнту."
        self.redaction_command_error = "Ти не маєш права це робити!"

        ##############    BUTTONS  #####################

        self.button_back = "Назад"

        self.button_start_work = "Розпочати"
        self.button_service_reviews = "Відгуки"
        self.button_service_info = "Інфо"
        self.button_service_what_special = "Що у мені особливого?"
        self.button_service_how_to_use = "Як мною користуватись?"

        self.button_tag_empty = "Каналів немає"

        self.button_channel_order = "Замовити"
        self.button_channel_forbidden_topics = "❗️Заборонені теми❗️"
        self.button_channel_statistic = "Статистика"
        self.button_channel_reviews = "Відгуки"

        self.button_order_my = "Мої замовлення"
        self.button_order_cancel = "Скасувати замовлення"
        self.button_order_no_photo = "У мене немає фото"
        self.button_order_send_to_redaction = "Надіслати редакції"
        
        self.button_redaction_new_order = "Переглянути"

        self.button_payment_refund = "REFUND"


        ##############    ETC  #####################

        self.oops = "Щось пішло не так :("
        self.under_development = "В розробці"
        self.delete_error = "Старі повідомлення неможливо видалити"

    def form_calendar_confirm_date(self, date):
        month = [
            "Січня", "Лютого", "Березня", "Квітня", "Травня", "Червня",
            "Липня", "Серпня", "Вересня", "Жовтня", "Листопада", "Грудня"
        ]
        msg = "Ви обрали дату замовлення на "
        msg += f"<b>{date.day} {month[date.month-1]}</b>"
        return msg

    def form_redaction_confirm_order(self, order_id):
        """
        'CONFIRMED' - notification for another bot
        """
        msg = f"/CONFIRMED_{order_id}"
        return msg

    def form_order_refund_info(self, channel_name, order_id, refund_amount):
        
        msg = "Кошти за не виконане замовлення повернено.\n\n"
        msg += f"<b>Order id</b> - {order_id}\n"
        msg += f"<b>Канал</b> - {channel_name.strip()}\n"
        msg += f"<b>Сума</b> - {refund_amount} UAH"

        return msg

    def form_order_receipt(self, channel_name, date, price):
        date = date.strftime("%d.%m.%Y")

        msg = "💡Нове замовлення реклами💡\n\n"
        msg += f"<b>Назва каналу</b> - {channel_name}\n"
        msg += f"<b>Дата</b> - {date}\n"
        msg += f"<b>Ціна</b> - {price} UAH\n\n"
        msg += "⚠️ Детальніше огляньте замовлення та проведіть оплату ⚠️\n" 
        msg += "У випадку порушення норм, ви отримаєте свої кошти назад протягом 12 годин🔙"

        return msg