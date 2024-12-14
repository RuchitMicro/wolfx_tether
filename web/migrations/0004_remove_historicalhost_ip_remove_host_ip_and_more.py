# Generated by Django 5.0 on 2024-12-14 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_remove_historicalhost_connect_script_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalhost',
            name='ip',
        ),
        migrations.RemoveField(
            model_name='host',
            name='ip',
        ),
        migrations.AddField(
            model_name='historicalhost',
            name='encrypted_pem',
            field=models.BinaryField(blank=True, help_text='Encrypted PEM file data.', null=True),
        ),
        migrations.AddField(
            model_name='historicalhost',
            name='host_address',
            field=models.CharField(help_text='Enter an host_address(ip) or domain name for the host.', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='historicalhost',
            name='use_credential',
            field=models.CharField(choices=[('password', 'Password'), ('pem', 'PEM File')], default='password', help_text='Specify whether to use a password or PEM file for authentication.', max_length=10),
        ),
        migrations.AddField(
            model_name='host',
            name='encrypted_pem',
            field=models.BinaryField(blank=True, help_text='Encrypted PEM file data.', null=True),
        ),
        migrations.AddField(
            model_name='host',
            name='host_address',
            field=models.CharField(help_text='Enter an host_address(ip) or domain name for the host.', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='host',
            name='use_credential',
            field=models.CharField(choices=[('password', 'Password'), ('pem', 'PEM File')], default='password', help_text='Specify whether to use a password or PEM file for authentication.', max_length=10),
        ),
        migrations.AlterField(
            model_name='historicalhost',
            name='name',
            field=models.CharField(help_text='Enter a unique name for the host.', max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='historicalhost',
            name='port',
            field=models.IntegerField(default=22, help_text='Specify the port number for SSH connections (default is 22).', null=True),
        ),
        migrations.AlterField(
            model_name='historicalhost',
            name='username',
            field=models.CharField(help_text='Enter the username for authenticating with the host.', max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='host',
            name='name',
            field=models.CharField(help_text='Enter a unique name for the host.', max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='host',
            name='port',
            field=models.IntegerField(default=22, help_text='Specify the port number for SSH connections (default is 22).', null=True),
        ),
        migrations.AlterField(
            model_name='host',
            name='username',
            field=models.CharField(help_text='Enter the username for authenticating with the host.', max_length=300, null=True),
        ),
    ]
