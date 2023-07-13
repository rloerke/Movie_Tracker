DROP TABLE if EXISTS movies;
CREATE TABLE movies (
    movieID integer primary key autoincrement unique,
    title text not null,
    description text,
    imdbRating integer,     --This is converted into a 1/100 rating before being entered into the database
    rtCriticRating integer,
    rtAudienceRating integer,
    metaRating integer
);