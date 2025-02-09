import json
from pydantic import BaseModel
from typing import List

class Artist(BaseModel):
    artist_name: str
    art_movement: str
    description: str
    notable_works: List[str]

class ExhibitingArtists(BaseModel):
    artists: List[Artist]

artist1 = Artist (
    artist_name="One",
    art_movement="One Movement", 
    description="One Art Description",
    notable_works=[
        "One Work 1",
        "One work 2"]
    )

artist2 = Artist (
    artist_name="Two",
    art_movement="Two Movement", 
    description="Two Art Description",
    notable_works=[
        "Two Work 1",
        "Two work 2"]
    )


stuff = ExhibitingArtists(artists=[artist1,artist2])

for index, thing in enumerate(stuff.artists):
    print(index, thing.artist_name)



