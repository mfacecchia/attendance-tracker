create table Utente(
	userID int not null auto_increment,
    Nome varChar(20) not null,
    Cognome varChar(20) not null,
    Tipologia varChar(30) not null check(Tipologia in('Admin', 'Studente', 'Insegnante')),
    ultimoLogin char(16) not null default 'Mai',
    
    primary key(userID)
);

create table Credenziali(
	Email varChar(40) not null,
    PW varChar(255) not null,
    googleID varChar(20) unique,
    githubID varChar(20) unique,
    userID int not null,
    
    primary key(Email),
    foreign key(userID) references Utente(userID) on delete cascade
);

create table Corso(
	idCorso int not null auto_increment,
    nomeCorso varChar(30) not null,
    annoCorso int not null,
    
    primary key(idCorso),
    unique(nomeCorso, annoCorso)
);

create table Lezione(
	idLezione int not null auto_increment,
    Materia varChar(30) not null,
    Descrizione varChar(1000),
    dataLezione date not null,
    oraInizio time not null default '09:00:00',
    oraFine time not null default '13:00:00',
    aula char(4) not null,
    Tipologia varChar(30) not null check(Tipologia in('Lezione', 'Seminario', 'Laboratorio')),
    idCorso int not null,
    idInsegnante int,
    
    primary key(idLezione),
    foreign key(idCorso) references Corso(idCorso) on delete cascade,
    foreign key(idInsegnante) references Utente(userID) on delete set null
);

create table Registrazione(
	userID int not null,
    idCorso int not null,
    
    foreign key(userID) references Utente(userID) on delete cascade,
    foreign key(idCorso) references Corso(idCorso) on delete cascade
);

create table Partecipazione(
	userID int not null,
    idLezione int not null,
    Presenza boolean not null default 0,
    
    foreign key(userID) references Utente(userID) on delete cascade,
    foreign key(idLezione) references Lezione(idLezione) on delete cascade
);