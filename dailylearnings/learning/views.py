from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import CreateDeckForm, CardForm, ProfileForm, UserForm, MessageForm
from .models import Deck, Subject, Card, Queue, Profile, Friends, Message
from dailylearnings.models import Page
from .functions import save_queue, get_next_times


# pk = primary key of user
@login_required(login_url='login')
def learning_page(request):
    # Decks that were personally created by the user
    my_decks = request.user.deck_set.all()

    # Decks that were not personally created by the user
    decks = Deck.objects.all()
    used_decks = []
    for deck in decks:
        user_list = deck.user.all()
        if request.user in user_list:
            used_decks.append(deck)

    context = {'page': Page.LEARNING.value, 'my_decks': my_decks, 'used_decks': used_decks}
    return render(request, 'learning/decks.html', context)


@login_required(login_url='login')
def analytics_page(request):

    queue = Queue.objects.filter(user_id=request.user.id)
    status = {
        'again': 0,
        'okay': 0,
        'easy': 0,
    }
    for q in queue:
        if q.learn_status == 'Again':
            status['again'] += 1
        elif q.learn_status == 'Okay':
            status['okay'] += 1
        else:
            status['easy'] += 1

    context = {'page': Page.LEARNING.value, 'status': status}
    return render(request, 'learning/analytics.html', context)


def profile_page(request, username):
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user_id=user)
    decks_of_user = Deck.objects.filter(creator=user.id)
    friends = Friends.objects.filter(Q(user_a=user) | Q(user_b=user))
    print(friends)

    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        profile.bio = request.POST.get('bio')
        profile.school = request.POST.get('school')
        subject = Subject.objects.get(id=request.POST.get('fav_subject'))
        profile.fav_subject = subject
        profile.save()
        context = {'page': Page.LEARNING.value, 'user': user, 'profile': profile, 'decks': decks_of_user}
        return render(request, 'learning/profile.html', context)

    if request.GET.get('edit-profile'):
        profile_form = ProfileForm(instance=profile)
        user_form = UserForm(instance=user)
        context = {'page': Page.LEARNING.value, 'user': user, 'profile': profile, 'decks': decks_of_user,
                   'edit_mode': True, 'profile_form': profile_form, 'user_form': user_form}
        return render(request, 'learning/profile.html', context)

    context = {'page': Page.LEARNING.value, 'user': user, 'profile': profile, 'decks': decks_of_user, 'friends': friends}
    return render(request, 'learning/profile.html', context)


@login_required(login_url='login')
def messages_page(request):
    received_messages = Message.objects.filter(recipient_id=request.user.id)
    sent_messages = Message.objects.filter(channel_id=request.user.id)

    context = {'page': Page.LEARNING.value, 'received_msg': received_messages, 'sent_msg': sent_messages}
    return render(request, 'learning/messages.html', context)


@login_required(login_url='login')
def write_message(request):
    form = MessageForm()

    if request.method == 'POST':
        recipient = User.objects.get(id=request.POST.get('recipient'))
        Message.objects.create(
            channel=request.user,
            recipient=recipient,
            title=request.POST.get('title'),
            type=request.POST.get('type'),
            message=request.POST.get('message'),
            read_msg=False,
        )
        return redirect('learning')

    context = {'page': Page.LEARNING.value, 'form': form}
    return render(request, 'learning/write-message.html', context)


@login_required(login_url='login')
def read_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user == message.recipient:
        message.read_msg = True
        message.save()
    elif request.user == message.channel:
        pass
    else:
        return redirect('learning')

    if request.POST.get('accept-friend-request'):
        Friends.objects.create(
            user_a=message.recipient,
            user_b=message.channel
        )
        message.delete()
        return redirect('learning')

    if request.POST.get('decline-friend-request'):
        message.delete()
        return redirect('learning')

    if request.POST.get('take-message-back'):
        message.delete()
        return redirect('messages')

    context = {'page': Page.LEARNING.value, 'message': message}
    return render(request, 'learning/read-message.html', context)


@login_required(login_url='login')
def settings_page(request, pk):
    deck = Deck.objects.get(id=pk)
    cards = Card.objects.filter(deck_id=pk)
    subjects = Subject.objects.all()

    if request.POST.get('save-deck-settings'):
        deck_name = request.POST.get('deck-name')
        subject_name = request.POST.get('deck-subject')
        subject, created = Subject.objects.get_or_create(name=subject_name)

        if not deck_name == '':
            deck.name = deck_name
            deck.subject = subject
            deck.public = True if request.POST.get('deck-public') == 'on' else False
            deck.save()
        print('Updated')

    # Delete the entire deck
    if request.POST.get('delete-deck'):
        Deck.objects.get(id=pk).delete()
        Card.objects.filter(deck_id=pk).delete()
        # DeckPosition.objects.filter(deck_id=pk).delete()
        return redirect('learning')

    # Delete a card
    if request.POST.get('delete-card'):
        # get ID of cards
        card_id = str(request.POST.get('delete-card'))[8:]
        Card.objects.get(id=card_id).delete()
        Queue.objects.filter(card_id=card_id).delete()
        redirect(f'settings/{pk}')

    if request.POST.get('unfollow-deck'):
        deck.user.remove(request.user)
        # DeckPosition.objects.filter(deck_id=pk, user_id=request.user).delete()
        return redirect('learning')

    context = {'page': Page.LEARNING.value, 'deck': deck, 'cards': cards, 'subjects': subjects}
    return render(request, 'learning/settings.html', context)


@login_required(login_url='login')
def edit_card_page(request, pk):
    card = Card.objects.get(id=pk)
    form = CardForm(instance=card)

    if request.user != card.deck.creator:
        return HttpResponse('You are not allowed here! [TEMP...]')

    if request.method == 'POST':
        card.question = request.POST.get('question')
        card.solution = request.POST.get('solution')
        card.save()
        return redirect('learning')

    context = {'page': Page.LEARNING.value, 'form': form, 'card': card}
    return render(request, 'learning/edit-card.html', context)


@login_required(login_url='login')
def create_deck(request):
    form = CreateDeckForm()
    subjects = Subject.objects.all()

    if request.method == 'POST':
        subject_name = request.POST.get('subject')
        subject, created = Subject.objects.get_or_create(name=subject_name)

        checkbox_input = request.POST.get('public')
        print(checkbox_input)

        Deck.objects.create(
            name=request.POST.get('deck_name'),
            creator=request.user,
            public=True if request.POST.get('public') == 'on' else False,
            subject=subject
        )
        return redirect('learning')

    context = {'page': Page.LEARNING.value, 'form': form, 'subjects': subjects}
    return render(request, 'learning/create-deck.html', context)


@login_required(login_url='login')
def learn_deck(request, pk):
    show_answer = False
    deck = Deck.objects.get(id=pk)
    queue = Queue.objects.filter(deck_id=deck.id, user_id=request.user).order_by('next_time')
    times = get_next_times(queue[0].time)

    try:
        card = Card.objects.get(id=queue[0].card_id)
    except:
        return passed_deck(request, pk)

    queues = Queue.objects.filter(deck_id=deck.id, user_id=request.user.id)
    status = {
        'again': 0,
        'okay': 0,
        'easy': 0
    }
    for q in queues:
        if q.learn_status == 'Again':
            status['again'] += 1
        elif q.learn_status == 'Okay':
            status['okay'] += 1
        else:
            status['easy'] += 1

    if request.GET.get('show'):
        show_answer = True

    if request.GET.get('again'):
        save_queue(queue[0], 'Again', 3)
        queue = Queue.objects.filter(deck_id=deck.id, user_id=request.user).order_by('next_time')
        card = Card.objects.get(id=queue[0].card_id)
        times = get_next_times(queue[0].time)

    if request.GET.get('okay'):
        save_queue(queue[0], 'Okay', 0.5)
        queue = Queue.objects.filter(deck_id=deck.id, user_id=request.user).order_by('next_time')
        card = Card.objects.get(id=queue[0].card_id)
        times = get_next_times(queue[0].time)

    if request.GET.get('easy'):
        save_queue(queue[0], 'Easy', 0.25)
        queue = Queue.objects.filter(deck_id=deck.id, user_id=request.user).order_by('next_time')
        card = Card.objects.get(id=queue[0].card_id)
        times = get_next_times(queue[0].time)

    if request.GET.get('edit-card'):
        form = CardForm(instance=card)
        context = {'page': Page.LEARNING.value, 'form': form, 'card': card}
        return render(request, 'learning/edit-card.html', context)

    if request.GET.get('skip-card'):
        save_queue(queue[0], 'Again', 0.25)
        queue = Queue.objects.filter(deck_id=deck.id, user_id=request.user).order_by('next_time')
        card = Card.objects.get(id=queue[0].card_id)
        times = get_next_times(queue[0].time)

    context = {'page': Page.LEARNING.value, 'deck': deck, 'card': card, 'queue': queue[0], 'status': status,
               'show_answer': show_answer, 'times': times}
    return render(request, 'learning/learn-deck.html', context)


@login_required(login_url='login')
def passed_deck(request, pk):
    deck = Deck.objects.get(id=pk)

    context = {'page': Page.LEARNING.value, 'deck': deck}
    return render(request, 'learning/passed-deck.html', context)


@login_required(login_url='login')
def add_card(request, pk):
    deck = Deck.objects.get(id=pk)

    form = CardForm(instance=deck)

    if request.user != deck.creator:
        return HttpResponse('You are not allowed here! [TEMP...]')

    if request.method == 'POST':
        card = Card.objects.create(
            deck=deck,
            question=request.POST.get('question'),
            solution=request.POST.get('solution')
        )
        Queue.objects.create(
            learn_status='Again',
            deck_id=deck.id,
            card_id=card.id,
            user_id=deck.creator.id,
            time='2m'
        )
        for user in deck.user.all():
            Queue.objects.create(
                learn_status='Again',
                deck_id=deck.id,
                card_id=card.id,
                user_id=user.id,
                time='2m'
            )

        return redirect('learning')

    context = {'page': Page.LEARNING.value, 'form': form, 'deck': deck}
    return render(request, 'learning/add-card.html', context)


def search_deck(request):
    if request.POST.get('search'):
        search_input = request.POST.get('search_input')
        decks = Deck.objects.filter(name__icontains=search_input, public=True)
        context = {'page': Page.LEARNING.value, 'search_input': search_input, 'decks': decks}
        return render(request, 'learning/search-deck.html', context)
    else:
        context = {'page': Page.LEARNING.value}
        return render(request, 'learning/search-deck.html', context)


def select_deck(request, pk):
    deck = Deck.objects.get(id=pk)

    if request.user == deck.creator:
        return redirect('learning')

    if request.method == 'POST':
        deck.user.add(request.user)
        cards = Card.objects.filter(deck_id=deck.id)
        for card in cards:
            Queue.objects.create(
                learn_status='Again',
                card_id=card.id,
                user_id=request.user.id,
                deck_id=deck.id,
                time='2m',
            )
        return redirect('learning')

    context = {'page': Page.LEARNING.value, 'deck': deck}
    return render(request, 'learning/select-deck.html', context)


def search_friend(request):

    user_profile = Profile.objects.get(id=request.user.id)

    if request.GET.get('search-user'):
        user_same_sub = Profile.objects.filter(fav_subject_id=user_profile.fav_subject).exclude(user_id=request.user.id)
        user_same_school = Profile.objects.filter(school=user_profile.school).exclude(user_id=request.user.id)

        context = {'page': Page.LEARNING.value, 'same_subject': user_same_sub, 'same_school': user_same_school}
        return render(request, 'learning/search-friends.html', context)

    context = {'page': Page.LEARNING.value, }
    return render(request, 'learning/search-friends.html', context)