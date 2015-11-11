from django.shortcuts import render, HttpResponseRedirect
from .forms import *
# from mysql.connector import connection
from django.db import connection
import math
from .data import *
# Create your views here.


def index(request):
    return render(request, 'chess/index.html')


def pushPlayers(request):
    name = None
    if Round.objects.count() > 1:
        register_close = True
        return render(request, 'chess/pushPlayers.html', {'register': register_close})
    else:
        form = PushPlayers()
        if request.method == 'POST':
            form = PushPlayers(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                form.save()
            else:
                form = PushPlayers()
        return render(request, 'chess/pushPlayers.html', {'form': form, 'name': name})


def pushed(request):
    players = RegisterPlayer.objects.raw('SELECT * FROM register ORDER BY register.name')
    players_count = RegisterPlayer.objects.count()

    if request.method == 'POST':
        form = AddPlaces(request.POST)
        if form.is_valid():
            places = form.cleaned_data['input_places']
            count_tour = round(math.log2(RegisterPlayer.objects.count())) + round(math.log2(places))

            #Добавление туров
            if Round.objects.count() == 0:
                with connection.cursor() as c:
                    for i in range(1, count_tour+1):
                        c.execute('INSERT INTO rounds VALUES (%s, %s)', [i, i])
                first_round = Round.objects.raw('SELECT * FROM rounds WHERE number=1')
            else:
                first_round = Round.objects.raw('SELECT * FROM rounds WHERE number=1')
    else:
        form = AddPlaces()
        count_tour = Round.objects.count()
        first_round = Round.objects.raw('SELECT * FROM rounds WHERE number=1')
    return render(request, 'chess/pushed.html', {'players': players, 'tour': count_tour, 'form': form,
                                                 'players_count': players_count, 'first_round': first_round})


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
    args['players_query'] = Player.objects.raw('SELECT * FROM players WHERE table_id=%s ORDER BY ello_rate DESC, '
                                                       'players.name ASC', [pk])
    get_id = []

    #Получение id игроков
    for i in args['players_query']:
        get_id.append(i.id)

    if len(get_id) == 1:
        result = 'Игроку добавлен 1 балл'
        cursor = connection.cursor()
        try:
            cursor.execute('UPDATE players SET result=%s WHERE id=%s', [1, get_id[0]])
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
                    cursor.execute('UPDATE players SET result=%s WHERE id=%s', [result[i], get_id[i]])
            finally:
                cursor.close()
            return HttpResponseRedirect('/chess/competition/round/{0}'.format(args['players_query'][0].round_id))
        else:
            form = PushResults()
    return render(request, 'chess/pushResult.html', {'data': args, 'form': form})


def addRound(request, pk):
    reg_player = RegisterPlayer.objects.count()
    get_players_pk = Player.objects.filter(round_id=int(pk)).count()

    if get_players_pk == 0:
        copy_players = RegisterPlayer.objects.raw('SELECT * FROM register')

        for i in copy_players:
            with connection.cursor() as c:
                c.execute('INSERT INTO players (id, name, ello_rate, result, round_id, table_id ) '
                          'VALUES (NULL, %s, %s, NULL, %s, NULL)', [i.name, i.ello_rate, int(pk)])

    cursor = connection.cursor()

    try:

        table_query = Table.objects.filter(round_id=pk).count()
        table_count = int(round(reg_player/2))

        table = Table.objects.raw('SELECT * FROM tables WHERE round_id_id=%s', [pk])

        if table_query == 0:
            for i in range(1, table_count + 1):
                cursor.execute('INSERT INTO tables VALUES (NULL , %s, %s)', [i, int(pk)])

        #Для 1го раунда
        if int(pk) == 1:
            first_part = Player.objects.raw('SELECT id, name, ello_rate FROM players ORDER BY ello_rate DESC '
                                                    'LIMIT %s', [table_count])
            second_part = Player.objects.raw('SELECT id, name, ello_rate FROM players ORDER BY ello_rate DESC '
                                                     'LIMIT %s, %s', [table_count, reg_player])

            #Запись игроку номера стола
            if first_part[0].table_id is None:
                for i in range(table_count):
                    first_player_id = first_part[i].id
                    second_player_id = second_part[i].id
                    cursor.execute('UPDATE players SET table_id=%s, round_id=%s WHERE id=%s', [i+1, int(pk), first_player_id])
                    cursor.execute('UPDATE players SET table_id=%s, round_id=%s WHERE id=%s', [i+1, int(pk), second_player_id])

        else:
            lose = Calculation(int(pk))

            lose.nextRound()

    finally:
        cursor.close()
    players = Player.objects.raw('SELECT * FROM players WHERE round_id=%s', [int(pk)])
    results = Player.objects.filter(result=None).count()

    d = makeQuery(2)
    print(d)
    if results == 0:
        next_round = int(pk) + 1

    else:
        next_round = 0
    return render(request, 'chess/addRound.html', {'players': players, 'tables': table, 'results': results, 'next_round':next_round})


def nextRound(limit, result):
    if limit % 2 != 0:
        print(result)
        player = RegisterPlayer.objects.raw('SELECT * FROM register WHERE result=%s '
                                            'ORDER BY ello_rate DESC, name ASC', [result])[0]
        print(player.id)
        with connection.cursor() as c:
            c.execute('UPDATE register SET result=%s WHERE id=%s', [result + 0.5, player.id])


def pushTable(limit, pk):
    cursor = connection.cursor()
    print(limit)
    try:
        first_part = RegisterPlayer.objects.raw('SELECT * FROM register '
                                                    'WHERE result=1 ORDER BY ello_rate DESC LIMIT %s',
                                                    [int(limit/2)])
        second_part = RegisterPlayer.objects.raw('SELECT * FROM register '
                                         'WHERE result=1 ORDER BY ello_rate DESC LIMIT %s, %s',
                                                      [int(limit/2), limit])
        for i in range(int(limit/2)):
            print(i)
            first_player_id = first_part[i].id
            second_player_id = second_part[i].id
            print(first_player_id)
            cursor.execute('UPDATE register SET table_id=%s, round_id=%s WHERE id=%s', [i+1, int(pk), first_player_id])
            cursor.execute('UPDATE register SET table_id=%s, round_id=%s WHERE id=%s', [i+1, int(pk), second_player_id])
    finally:
        cursor.close()