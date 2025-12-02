from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Room

class RoomListView(ListView):
    model = Room
    template_name = 'room_list.html'
    context_object_name = 'rooms'


class RoomDetailView(DetailView):
    model = Room
    template_name = 'core/room_detail.html'
    context_object_name = 'room'
