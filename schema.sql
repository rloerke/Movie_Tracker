DROP TABLE if EXISTS movies;
CREATE TABLE movies (
    movieID integer primary key autoincrement unique,
    title text not null,
    description text,
    imdbRating integer,
    rtCriticRating integer,
    rtAudienceRating integer,
    metaRating integer
);

INSERT INTO movies (title, description, imdbRating, rtCriticRating, rtAudienceRating, metaRating) VALUES ("Inception",
"A group of people try to plant an idea in someones head through their dreams", "88", "87", "91", "74");

INSERT INTO movies (title, description, imdbRating, rtCriticRating, rtAudienceRating, metaRating) VALUES (
"Grosse Pointe Blank", "A professional hitman attends his high school reunion", "73", "76", "82", "87");