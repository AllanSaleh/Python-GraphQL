import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from models import Movie as MovieModel, db

class Movie(SQLAlchemyObjectType):
    class Meta:
        model = MovieModel

class Query(graphene.ObjectType):
    movies = graphene.List(Movie)
    search_movies = graphene.List(Movie, title=graphene.String(), director=graphene.String(), year=graphene.Int())

    def resolve_movies(self, info):
        return db.session.execute(db.select(MovieModel)).scalars()
    
    def resolve_search_movies(self, info, title=None, director=None, year=None):
        query = db.select(MovieModel)
        if title:
            query = query.where(MovieModel.title.ilike(f'%{title}%'))
        if director:
            query = query.where(MovieModel.director.ilike(f'%{director}%'))
        if year:
            query = query.where(MovieModel.year == year)
        results = db.session.execute(query).scalars().all()
        return results


class AddMovie(graphene.Mutation): #Creating our addMovie Mutation
    class Arguments: #the arguments required to add a movie
        title = graphene.String(required=True)
        director = graphene.String(required=True)
        year = graphene.Int(required=True)
    
    movie = graphene.Field(Movie)

    def mutate(self, info, title, director, year): #This is the function that runs when the mutation is called
        movie = MovieModel(title=title, director=director, year=year) #Creating an instance of MovieModel
        db.session.add(movie)
        db.session.commit() #add movie to our database

        db.session.refresh(movie) #just incase the movie becomes detached from our session
        return AddMovie(movie=movie)
    
class UpdateMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String(required=False) #making it not required to have these fields so we can update specific pieces of info
        director = graphene.String(required=False)
        year = graphene.Int(required=False)

    movie = graphene.Field(Movie)

    def mutate(self, info, id, title=None, director=None, year=None):
        movie = db.session.get(MovieModel, id)
        if not movie:
            return None
        if title:
            movie.title = title
        if director:
            movie.director = director
        if year:
            movie.year = year

        db.session.add(movie)
        db.session.commit()
        return UpdateMovie(movie=movie)
    
class DeleteMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    movie = graphene.Field(Movie)

    def mutate(self, info, id):
        movie = db.session.get(MovieModel, id)
        if movie:
            db.session.delete(movie)
            db.session.commit()
        else:
            return None
        
        return DeleteMovie(movie=movie)

class Mutation(graphene.ObjectType):
    create_movie = AddMovie.Field()
    update_movie = UpdateMovie.Field()
    delete_movie = DeleteMovie.Field()
