CREATE SEQUENCE users_id_seq;
CREATE TABLE IF NOT EXISTS users (
  id INT NOT NULL DEFAULT nextval('users_id_seq'),
  name varchar(256) NOT NULL,
  email varchar(256) NOT NULL,
  PRIMARY KEY (id)
);
ALTER SEQUENCE users_id_seq OWNED BY users.id;
