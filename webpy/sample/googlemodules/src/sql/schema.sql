create table modules (
    id                      int(11) not null auto_increment,
    datetime_created        timestamp default current_timestamp,
    title                   varchar(250) not null default '',
    description             text not null,
    title_url               varchar(250) not null default '',
    author                  varchar(100) not null default '',
    author_email            varchar(100) not null default '',
    author_affiliation      varchar(100) not null default '',
    datetime_updated        datetime not null default '0000-00-00 00:00:00',
    calculated_vote         float not null default '-1',
    author_location         varchar(100) not null default '',
    screenshot              varchar(50) not null default '',
    url                     varchar(250) not null default '',
    staffpick               char(1) binary not null default '0',
    cached_xml              text not null,
    render_inline           varchar(8) not null default 'never',
    primary key             (id),
    unique key              screenshot (screenshot),
    unique key              url (url)
) engine=InnoDB; charset utf8;

create table tags (
    id                      int(11) not null auto_increment,
    module_id               int(11) not null default '0',
    tag                     varchar(50) not null default '',
    primary key             (id)
) engine=InnoDB; charset utf8;

create table votes (
    id                      int(11) not null auto_increment,
    vote                    tinyint(4) not null default '0',
    module_id               int(11) not null default '0',
    ip                      varchar(15) not null default '',
    datetime_created        timestamp default current_timestamp,
    primary key             (id)
) engine=InnoDB; charset utf8;

create table comments (
    id                      int(11) not null auto_increment,
    module_id               int(11) not null default '0',
    datetime_created        timestamp default current_timestamp,
    author                  varchar(100) not null default '',
    content                 text not null,
    primary key             (id)
) engine=InnoDB; charset utf8;

create table forum_threads (
    id                      int(11) not null auto_increment,
    author                  varchar(100) not null default '',
    title                   varchar(200) not null default '',
    content                 text not null,
    datetime_created        timestamp default current_timestamp,
    reply_to                int(11) not null default '0',
    primary key             (id)
) engine=InnoDB; charset utf8;
alter table forum_threads add index (reply_to);
