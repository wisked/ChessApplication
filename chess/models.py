from django.db import models

# Create your models here.


class Round(models.Model):
    number = models.PositiveIntegerField()

    class Meta:
        db_table = 'rounds'


class Table(models.Model):
    round_id = models.ForeignKey(Round)
    number_table = models.PositiveIntegerField()

    class Meta:
        db_table = 'tables'


class Player(models.Model):
    table_id = models.IntegerField(null=True)
    round_id = models.IntegerField(null=True)
    name = models.CharField(max_length=50)
    ello_rate = models.FloatField(default=0)
    result = models.FloatField(null=True)

    class Meta:
        db_table = 'players'
        ordering = ['ello_rate']


class RegisterPlayer(models.Model):
    MATCH_RESULT = (
        (1, 'Победа'),
        (0.5, 'Ничья'),
        (0, 'Проигрыш'),
    )

    name = models.CharField(max_length=50)
    ello_rate = models.FloatField(default=0)
    result = models.FloatField(choices=MATCH_RESULT, null=True)
    table_id = models.IntegerField(blank=True, null=True)
    round_id = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'register'
