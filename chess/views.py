from django.shortcuts import render, HttpResponseRedirect
from .forms import *
# from mysql.connector import connection
from django.db import connection
import math
# Create your views here.


def index(request):
    return render(request, 'chess/index.html')


def pushPlayers(request):
    if Round.objects.count() > 0:
        register = True
        return render(request, 'chess/pushPlayers.html', {'register': register})
    else:
        form = PushPlayers()
        if request.method == 'POST':
            form = PushPlayers(request.POST)
            name = None
            if form.is_valid():
                name = form.cleaned_data['name']
                form.save()
            else:
                form = PushPlayers()
        return render(request, 'chess/pushPlayers.html', {'form': form, 'name': name})


def pushed(request):
    players = RegisterPlayer.objects.raw('SELECT * FROM register ORDER BY register.name')
    players_count = RegisterPlayer.objects.count()
    count_tour = 0
    if request.method == 'POST':
        form = AddPlaces(request.POST)
        if form.is_valid():
            places = form.cleaned_data['input_places']
            count_tour = round(math.log2(RegisterPlayer.objects.count())) + round(math.log2(places))
    else:
        form = AddPlaces()

    return render(request, 'chess/pushed.html', {'players': players, 'tour': count_tour, 'form': form,
                                                 'players_count': players_count})


def startCompetition(request):
    reg_player = RegisterPlayer.objects.count()
    cursor = connection.cursor()
    try:
        cursor.execute('SELECT * FROM rounds')
        round_count = cursor.fetchone()

        #Создание 1го раунда
        if round_count == None:
            cursor.execute('INSERT INTO rounds VALUES (1,1)')

        table_query = Table.objects.raw('SELECT * FROM tables') #?
        table_count = int(round(reg_player/2))

        #Добавление столов
        if Table.objects.count() == 0:
            for i in range(1, table_count+1):
                cursor.execute('INSERT INTO tables VALUES (%s, %s, 1)', [i, i])

        # get_table_id = RegisterPlayer.objects.raw('SELECT * from register WHERE result is NULL LIMIT 1')
        first_part = RegisterPlayer.objects.raw('SELECT id, name, ello_rate FROM register ORDER BY ello_rate DESC '
                                                'LIMIT %s', [table_count])
        second_part = RegisterPlayer.objects.raw('SELECT id, name, ello_rate FROM register ORDER BY ello_rate DESC '
                                                'LIMIT %s, %s', [table_count, reg_player])

        #Запись игроку номера стола
        if first_part[0].table_id is None:
            for i in range(table_count):
                first_player_id = first_part[i].id
                second_player_id = second_part[i].id
                # get_pair = RegisterPlayer.objects.raw('SELECT * FROM register WHERE table_id is NULL '
                #                                       'ORDER BY ello_rate DESC LIMIT 2')
                # for var in get_pair:
                cursor.execute('UPDATE register SET table_id=%s WHERE id=%s', [i+1, first_player_id])
                cursor.execute('UPDATE register SET table_id=%s WHERE id=%s', [i+1, second_player_id])
        cursor.execute('SELECT id, result FROM register WHERE result IS NULL')
        get_result = cursor.fetchone()
    finally:
        cursor.close()
    get_players = RegisterPlayer.objects.raw('SELECT * FROM register ORDER BY ello_rate DESC')
    # get_result = RegisterPlayer.objects.raw('SELECT id, result FROM register WHERE result IS NULL')
    # get_result = RegisterPlayer.objects.raw('SELECT COUNT (id, result) FROM register WHERE result IS NULL')

    return render(request, 'chess/startCompetition.html', {'round': round_count, 'data': get_players, 'tables': table_query,
                                                           'result': get_result})


def pushResult(request, pk):
    args = {}
    args['players_query'] = RegisterPlayer.objects.raw('SELECT * FROM register WHERE table_id=%s ORDER BY ello_rate', [pk])
    get_id = []
    #Получение id игроков
    for i in args['players_query']:
        get_id.append(i.id)

    if len(get_id) == 1:
        result = 'Игроку добавлен 1 балл'
        cursor = connection.cursor()
        try:
            cursor.execute('UPDATE register SET result=%s WHERE id=%s', [1, get_id[0]])
        finally:
            cursor.close()
        return HttpResponseRedirect('/chess/start/')
    else:
        form = PushResults()

    if request.method == 'POST':
        form = PushResults(request.POST)
        if form.is_valid():
            result = []
            result.append(form.cleaned_data['first_result'])
            result.append(form.cleaned_data['second_result'])

            cursor = connection.cursor()
            try:
                for i in range(len(get_id)):
                    cursor.execute('UPDATE register SET result=%s WHERE id=%s', [result[i], get_id[i]])
            finally:
                cursor.close()
            return HttpResponseRedirect('/chess/start')
        else:
            form = PushResults()
    return render(request, 'chess/pushResult.html', {'data': args, 'form': form})


def addRound(request, pk):
    print(pk)
    new_key = int(pk + 1)
    Round.objects.raw('INSERT INTO rounds VALUES (%s,%s)', [new_key, new_key])
    reg_players = RegisterPlayer.objects.count()
    table_count = int(round(reg_players/2))
    cursor = connection.cursor()
    try:
        players = RegisterPlayer.objects.raw('SELECT * FROM register')
        for i in players:
            cursor.execute('INSERT INTO players VALUES (%s, %s, %s, %s, %s)', [i.id, i.name, i.ello_rate, i.table_id, i.result])

        #Добавление столов
        # if Table.objects.count() == 0:
        #     for i in range(1, table_count+1):
        #         cursor.execute('INSERT INTO tables VALUES (%s, %s, %s)', [i, i, pk])

        # get_table_id = RegisterPlayer.objects.raw('SELECT * from register WHERE result is NULL LIMIT 1')
        # first_part = RegisterPlayer.objects.raw('SELECT id, name, ello_rate FROM register ORDER BY ello_rate DESC '
        #                                         'LIMIT %s', [table_count])
        # second_part = RegisterPlayer.objects.raw('SELECT id, name, ello_rate FROM register ORDER BY ello_rate DESC '
        #                                         'LIMIT %s, %s', [table_count, reg_players])
    finally:
        cursor.close()

    return render(request, 'chess/addRound.html')