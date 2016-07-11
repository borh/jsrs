from hypothesis.extra.django.models import models
from hypothesis import given

from ..models import User, Rater


@given(models(Rater, user=models(User)))
def test_rater_survey(rater):
    # generate rater from user
    print(rater.example())

    # send POST requests to survey

    # compare data in database with generated data

    # make sure that having done the survey, the user is redirected to the ratings page
    return False
