-- Oracle Database 19c

CREATE USER pyportforward IDENTIFIED BY 'ppf';
GRANT CONNECT, RESOURCE TO pyportforward;

CREATE TABLE pyportforward.user(
    userid VARCHAR2(32) NOT NULL,
    username VARCHAR2(50) NOT NULL,
    password VARCHAR2(64) NOT NULL,
    email VARCHAR2(50) NOT NULL,
    role VARCHAR2(50) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
CREATE UNIQUE INDEX user_userid_uindex ON pyportforward.user(userid);

CREATE TABLE pyportforward.connectionlog(
    userid VARCHAR2(32) NOT NULL,
    clientid VARCHAR2(32) NOT NULL,
    clientip VARCHAR2(40) NOT NULL,
    clinetport NUMBER NOT NULL,
    connectionid VARCHAR2(32) NOT NULL,
    connected_at TIMESTAMP NOT NULL,
    status VARCHAR2(15) NOT NULL
);
CREATE UNIQUE INDEX connectionlog_userid ON pyportforward.connectionlog(userid, clientid, connectionid);

CREATE TABLE pyportforward.origin(
    userid VARCHAR2(32) NOT NULL,
    connectionid VARCHAR2(32) NOT NULL,
    connectionip VARCHAR2(40) NOT NULL,
    connectionport NUMBER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
CREATE UNIQUE INDEX origin_userid ON pyportforward.origin(userid, connectionid);

CREATE TABLE pyportforward.origin_history(
    userid VARCHAR2(32) NOT NULL,
    connectionid VARCHAR2(32) NOT NULL,
    connectionip VARCHAR2(40) NOT NULL,
    connectionport NUMBER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- trigger when origin deleted, move to origin_history
CREATE OR REPLACE TRIGGER origin_delete_trigger
AFTER DELETE ON pyportforward.origin
FOR EACH ROW
BEGIN
    INSERT INTO pyportforward.origin_history(userid, connectionid, connectionip, connectionport, created_at, updated_at)
    VALUES(:OLD.userid, :OLD.connectionid, :OLD.connectionip, :OLD.connectionport, :OLD.created_at, SYSDATE);
END;
/


--SELECT connectionid FROM pyportforward.origin_history A WHERE updated_at > SYSDATE - 1;
--SELECT connectionid FROM pyportforward.origin B;
--SELECT clientid FROM pyportforward.connectionlog C WHERE connected_at > SYSDATE - 1;
