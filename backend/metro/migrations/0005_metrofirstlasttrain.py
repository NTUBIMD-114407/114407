from django.db import migrations, models




class Migration(migrations.Migration):


    dependencies = [
        ('metro', '0004_stationid'),
    ]


    operations = [
        migrations.CreateModel(
            name='MetroFirstLastTrain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line_no', models.CharField(max_length=10, verbose_name='路線編號')),
                ('line_id', models.CharField(max_length=10, verbose_name='路線ID')),
                ('station_id', models.CharField(max_length=10, verbose_name='站點ID')),
                ('station_name', models.CharField(max_length=100, verbose_name='站點名稱')),
                ('station_name_en', models.CharField(max_length=100, verbose_name='站點英文名稱')),
                ('trip_head_sign', models.CharField(max_length=100, verbose_name='列車方向')),
                ('destination_station_id', models.CharField(max_length=10, verbose_name='目的地站點ID')),
                ('destination_station_name', models.CharField(max_length=100, verbose_name='目的地站點名稱')),
                ('destination_station_name_en', models.CharField(max_length=100, verbose_name='目的地站點英文名稱')),
                ('train_type', models.IntegerField(verbose_name='列車類型')),
                ('first_train_time', models.TimeField(verbose_name='首班車時間')),
                ('last_train_time', models.TimeField(verbose_name='末班車時間')),
                ('monday', models.BooleanField(default=True, verbose_name='週一')),
                ('tuesday', models.BooleanField(default=True, verbose_name='週二')),
                ('wednesday', models.BooleanField(default=True, verbose_name='週三')),
                ('thursday', models.BooleanField(default=True, verbose_name='週四')),
                ('friday', models.BooleanField(default=True, verbose_name='週五')),
                ('saturday', models.BooleanField(default=True, verbose_name='週六')),
                ('sunday', models.BooleanField(default=True, verbose_name='週日')),
                ('national_holidays', models.BooleanField(default=True, verbose_name='國定假日')),
                ('src_update_time', models.DateTimeField(verbose_name='來源更新時間')),
                ('update_time', models.DateTimeField(verbose_name='更新時間')),
                ('version_id', models.IntegerField(verbose_name='版本ID')),
            ],
            options={
                'verbose_name': '捷運首末班車',
                'verbose_name_plural': '捷運首末班車',
                'ordering': ['line_no', 'station_id', 'first_train_time'],
                'unique_together': {('line_no', 'station_id', 'destination_station_id', 'train_type')},
            },
        ),
    ]



