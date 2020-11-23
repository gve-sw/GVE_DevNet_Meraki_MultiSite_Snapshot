DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS snaps;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  accessToken TEXT NOT NULL
);

CREATE TABLE snaps (
  id INTEGER,
  url TEXT,
  expire TEXT,
  network TEXT,
  timestamp TEXT,
  camera TEXT,
  localURL TEXT PRIMARY KEY,
  FOREIGN KEY (id) REFERENCES user (id)
);
