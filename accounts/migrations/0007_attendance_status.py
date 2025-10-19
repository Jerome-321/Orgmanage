from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_achievement_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('Present', 'Present'),
                    ('Absent', 'Absent'),
                    ('Late', 'Late'),
                ],
                default='Absent',
            ),
        ),
    ]