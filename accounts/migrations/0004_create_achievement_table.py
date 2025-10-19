from django.db import migrations, models
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_remove_event_capacity_alter_event_location'),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('date_awarded', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=models.CASCADE, related_name='achievements', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
