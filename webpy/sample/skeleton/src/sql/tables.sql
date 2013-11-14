CREATE TABLE items (
    id serial primary key,
    author_id int references users,
    body text,
    created timestamp default current_timestamp 
);
