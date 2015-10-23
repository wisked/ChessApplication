from django.shortcuts import render, HttpResponseRedirect
from .forms import *
# from mysql.connector import connection
from django.db import connection
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

            if form.is_valid():
                name = form.cleaned_data['name']
                form.save()
            else:
                form = PushPlayers()
        return render(request, 'chess/pushPlayers.html', {'form': form})


def pushed(request):
    players = RegisterPlayer.objects.raw('SELECT * FROM register ORDER BY register.name')
    return render(request, 'chess/pushed.html', {'players': players})


def startCompetition(request):
    reg_player = RegisterPlayer.objects.count()
    cursor = connection.cursor()
    try:
        cursor.execute('SELECT * FROM rounds')
        round_count = cursor.fetchone()

        #Создание 1го раунда
        if round_count == None:
            cursor.execute('INSERT INTO rounds VALUES (1,1)')

        table_query = Table.objects.raw('SELECT * FROM tables')
        table_count = int(round(reg_player/2))

        #Добавление столов
        if table_query[0].id == None:
            for i in range(1, table_count+1):
                cursor.execute('INSERT INTO tables VALUES (%s, %s, 1)', [i, i])

        get_table_id = RegisterPlayer.objects.raw('SELECT * from register WHERE id = 1')

        #Запись игроку номера стола
        if get_table_id[0].table_id is 'NULL':
            for i in range(1, table_count+1):
                get_pair = RegisterPlayer.objects.raw('SELECT * FROM register WHERE table_id is NULL '
                                                      'ORDER BY ello_rate DESC LIMIT 2')
                for var in get_pair:
                    cursor.execute('UPDATE register SET table_id=%s WHERE id=%s', [i, var.id])
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
