DROP TABLE IF EXISTS Tag_Word;
DROP TABLE IF EXISTS Tag_Info;
DROP TABLE IF EXISTS Barcode_Info;

CREATE TABLE Tag_Info
(
	TagId BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    ImportDate VARCHAR(10) NOT NULL DEFAULT (DATE_FORMAT(NOW(),'%Y-%m-%d')),
    OriginalImagePath VARCHAR(255) NOT NULL,
    ProcessingTime DECIMAL(9,3),
    Img LONGBLOB NOT NULL
);

CREATE TABLE Tag_Word
(
    TagId BIGINT,
    WordIndex INT,
    OCRDescription VARCHAR(50) NOT NULL,
    Replacement VARCHAR(50) NOT NULL,
    Suggestions VARCHAR(1000) NOT NULL,
    Vertices VARCHAR (500) NOT NULL,
    Category VARCHAR(50) NOT NULL,
    LastUpdatedTimeStamp DATETIME DEFAULT NOW(),
    FOREIGN KEY(TagId) REFERENCES Tag_Info(TagId),
    PRIMARY KEY (TagId, WordIndex)
);

CREATE TABLE Barcode_Info
(
    BarCode VARCHAR(10),
    IRN BIGINT,
    Taxonomy VARCHAR(100),
    Collector VARCHAR(100),
    Details VARCHAR(1000),
    PRIMARY KEY (BarCode)
);
