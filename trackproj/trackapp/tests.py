from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Track

# This checks if the Track model is created correctly and if the fields are correct.
class TrackModelTests(TestCase):
    def test_track_creation(self):
        track = Track.objects.create(
            label="Trilha de Teste",
            description="You put your left foot in, you put your left foot out",
            difficulty="Fácil",
            duration=60,
            route_type="Ida e Volta",
            elevation=100
        )
        self.assertEqual(track.label, "Trilha de Teste")
        self.assertEqual(track.difficulty, "Fácil")
        self.assertEqual(track.description, "You put your left foot in, you put your left foot out")
        self.assertEqual(track.duration, 60)
        self.assertEqual(track.route_type, "Ida e Volta")
        self.assertEqual(track.elevation, 100)

# This checks if the API is working.
class TrackAPITests(APITestCase):
    def setUp(self):
        self.track = Track.objects.create(
            label="Trilha de Teste 2",
            description="You put your right foot in, and you shake it all about.",
            difficulty="Moderado",
            duration=60,
            route_type="Ida",
            elevation=100
        )
    
    def test_get_tracks(self):
        url = reverse('track-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['label'], "Trilha de Teste 2")
        self.assertEqual(response.data['results'][0]['difficulty'], "Moderado")
