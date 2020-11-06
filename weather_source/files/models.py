import peewee
from playhouse.db_url import connect
from weather_source.functions_subworkers import LOG

database_proxy = peewee.DatabaseProxy()


class BaseTable(peewee.Model):
    class Meta:
        database = database_proxy


class Temperature(BaseTable):
    """прогноз погоды на определёный день, город"""
    date = peewee.DateTimeField()
    city = peewee.CharField()
    part_day = peewee.CharField()
    temp = peewee.CharField()
    weather = peewee.CharField()


class DatabaseUpdater:
    def base_init(self, name_db):
        if name_db == 'DEBUG':
            database = connect('sqlite:///weather_table.db')
        elif name_db == "TEST":
            database = peewee.SqliteDatabase(':memory:')
        else:
            database = peewee.SqliteDatabase('mega_production_db')
        database_proxy.initialize(database)
        try:
            database_proxy.create_tables([Temperature])
        except peewee.OperationalError:
            print("Table already exists!")

    def base_puller(self, date_weather, city):
        """выгрузка данных с БД"""
        for date_bd in Temperature.select().where(Temperature.city == city):
            if len(date_weather) == 2:
                if date_weather[0] <= date_bd.date.date() <= date_weather[1]:
                    yield date_bd.city, date_bd.date, date_bd.part_day, \
                          {'weather': date_bd.weather, 'temp': date_bd.temp}
            else:
                if date_bd.date.date() == date_weather[0]:
                    yield date_bd.city, date_bd.date, date_bd.part_day, {'weather': date_bd.weather,
                                                                         'temp': date_bd.temp}

    def base_pusher(self, date_weather, part_day, weather, city):
        """загрузка данных в БД"""
        get_id, created = Temperature.get_or_create(
            date=date_weather,
            part_day=part_day,
            city=city,
            defaults={'temp': weather['temp'], 'weather': weather['weather']})

        if not created:
            updated = Temperature.update({'weather': weather['weather'], 'temp': weather['temp']}). \
                where(Temperature.id == get_id)
            LOG.info(f'Обновлено: {updated.execute()} - {Temperature.date} - {Temperature.part_day}')

    def close(self):
        print(f'БД :«На этом мои полномочия всё»')
