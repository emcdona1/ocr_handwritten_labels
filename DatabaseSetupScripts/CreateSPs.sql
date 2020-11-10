
DROP PROCEDURE IF EXISTS SP_AddTag;
DROP PROCEDURE IF EXISTS SP_UpdateWord;
DROP PROCEDURE IF EXISTS SP_DeleteTag;
DROP PROCEDURE IF EXISTS SP_GetTagList;
DROP PROCEDURE IF EXISTS SP_GetTagDetail;
DROP PROCEDURE IF EXISTS SP_AddBarCodeInfo;
DROP PROCEDURE IF EXISTS SP_GetBarCodeInfo;
DROP PROCEDURE IF EXISTS SP_GetImportDates;
DROP PROCEDURE IF EXISTS SP_AddUpdateTagClassification;
DROP PROCEDURE IF EXISTS SP_GetTagClassification;

DELIMITER $$

 CREATE PROCEDURE SP_AddTag(
	IN originalImagePathIn VARCHAR(255),
    IN processingTimeIn DECIMAL(9,3),
    IN imgIn LONGBLOB,
    IN wordsInfoAsXMLIn LONGTEXT,
    IN barCodeIn VARCHAR(20)
 )
 BEGIN
	SET @ImportDate=(SELECT DATE_FORMAT(NOW(),'%Y-%m-%d'));
	INSERT INTO Tag_Info(BarCode,ImportDate,OriginalImagePath,ProcessingTime,Img)
	VALUES (barCodeIn,@ImportDate,originalImagePathIn,processingTimeIn,UNHEX(imgIn));
	SELECT LAST_INSERT_ID() INTO @newTagId;
    
	SET @COUNT = (SELECT EXTRACTVALUE(wordsInfoAsXMLIn,'COUNT(//words/word)'));
    SET @I = 1;
    WHILE(@I <= @COUNT) DO

        INSERT INTO Tag_Word(TagId,WordIndex,OCRDescription,Replacement,Suggestions,Vertices,Category)
        SELECT  @newTagId,
				ExtractValue(wordsInfoAsXMLIn,CONCAT('/words/word[',@I,']/wordIndex')),
				ExtractValue(wordsInfoAsXMLIn,CONCAT('/words/word[',@I,']/description')),
                ExtractValue(wordsInfoAsXMLIn,CONCAT('/words/word[',@I,']/replacement')),
                ExtractValue(wordsInfoAsXMLIn,CONCAT('/words/word[',@I,']/suggestions')),
                ExtractValue(wordsInfoAsXMLIn,CONCAT('/words/word[',@I,']/vertices')),
                ExtractValue(wordsInfoAsXMLIn,CONCAT('/words/word[',@I,']/category'));
        SET @I = @I + 1;
    END WHILE;
    IF EXISTS (SELECT 1 FROM  Barcode_Info where Barcode=barCodeIn)
    THEN SELECT @newTagId,@ImportDate,1;
    ELSE SELECT @newTagId,@ImportDate,0;
    END IF;
 END $$ 
  
 DELIMITER $$
 CREATE PROCEDURE SP_UpdateWord(
	IN tagidIn BIGINT,
	IN wordIndexIn INT,
	IN replacementIn VARCHAR(50) ,
    IN suggestionsIn VARCHAR(1000),
    IN categoryIn VARCHAR(50)
 )
 BEGIN
	UPDATE Tag_Word tw
    SET tw.Replacement=replacementIn,
		tw.Suggestions=suggestionsIn,
		tw.Category=categoryIn,
        tw.LastUpdatedTimeStamp=NOW()
    WHERE tw.WordIndex=wordIndexIn and tw.TagId=tagidIn;
 END $$
 
DELIMITER $$
 CREATE PROCEDURE SP_DeleteTag(
	IN tagIdDelete BIGINT
 )
 BEGIN
	DELETE FROM Tag_ClassifiedInfo where TagId=tagIdDelete;
	DELETE FROM Tag_Word WHERE TagId=tagIdDelete;
    DELETE FROM Tag_Info WHERE TagId=tagIdDelete;
END $$

DELIMITER $$
 CREATE PROCEDURE SP_GetTagList(
	IN importDateIn VARCHAR(20),
    IN sortItemsByBarCode BIT,
    IN startIndexIn BIGINT,
    IN countIn BIGINT
 )
 BEGIN
	DROP TABLE IF EXISTS TagListTempTable;
	CREATE TEMPORARY TABLE TagListTempTable (
		Position BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
        TagId BIGINT,
        BarCode VARCHAR(20),
		ImportDate VARCHAR(10),
		OriginalImagePath VARCHAR(255)
	) ENGINE=MEMORY;
    
	IF sortItemsByBarCode=1 
    THEN 
		INSERT INTO TagListTempTable (TagId,BarCode,ImportDate,OriginalImagePath)
		SELECT ti.TagId, ti.BarCode,ti.ImportDate,ti.OriginalImagePath FROM Tag_info ti
		WHERE importDateIn in ('Filter: None', ti.ImportDate) order by ti.BarCode;	
    ELSE 
		INSERT INTO TagListTempTable
		SELECT ti.TagId, ti.BarCode,ti.ImportDate,ti.OriginalImagePath FROM Tag_info ti
		WHERE importDateIn in ('Filter: None', ti.ImportDate) order by ti.TagId;	
    END IF;
    
    SELECT TagId,BarCode,ImportDate,OriginalImagePath FROM TagListTempTable tl
    WHERE tl.Position>startIndexIn LIMIT countIn;
    DROP TABLE TagListTempTable; 
 END $$
 
 DELIMITER $$
 CREATE PROCEDURE SP_GetImportDates()
 BEGIN
	SELECT ImportDate, count(1) from Tag_info group by ImportDate order by ImportDate;
 END $$
 
 DELIMITER $$
 
 CREATE PROCEDURE SP_GetTagDetail(
	IN tagIdIn BIGINT
 )
 BEGIN
	SELECT ti.Img, ti.OriginalImagePath,ti.ProcessingTime,ti.ImportDate,ti.BarCode
    FROM Tag_Info ti 
    WHERE ti.TagId=tagidIn;
	SELECT WordIndex,OCRDescription,Replacement,Suggestions,Vertices,Category FROM Tag_Word w Where w.TagId=tagIdIn;
 END $$
 
 
 DELIMITER $$
 CREATE PROCEDURE SP_AddBarCodeInfo(
	IN barCodeIn VARCHAR(10),
	IN classificationInfoAsXML LONGTEXT
)
BEGIN
	IF NOT EXISTS (SELECT * FROM Barcode_Info WHERE BarCode=barCodeIn)
	THEN
		SET @COUNT = (SELECT EXTRACTVALUE(classificationInfoAsXML,'COUNT(//classifications/classification)'));
		SET @I = 1;
		WHILE(@I <= @COUNT) DO
			INSERT INTO Barcode_Info(BarCode,Category,Information)
			SELECT  barCodeIn,
					ExtractValue(classificationInfoAsXML,CONCAT('/classifications/classification[',@I,']/Category')),
					ExtractValue(classificationInfoAsXML,CONCAT('/classifications/classification[',@I,']/Information'));
			SET @I = @I + 1;
		END WHILE;
    END IF;
 END $$ 

DELIMITER $$
 CREATE PROCEDURE SP_GetBarCodeInfo(
	IN barCodeIn VARCHAR(10)
)
BEGIN
	SELECT Category,Information FROM Barcode_Info where BarCode=barCodeIn order by Category;
END $$ 

 DELIMITER $$
 CREATE PROCEDURE SP_AddUpdateTagClassification(
	IN TagIdIn BIGINT,
    IN classificationInfoAsXML LONGTEXT
)
BEGIN
	DELETE FROM Tag_ClassifiedInfo where TagId=TagIdIn;

	SET @COUNT = (SELECT EXTRACTVALUE(classificationInfoAsXML,'COUNT(//classifications/classification)'));
    SET @I = 1;
    WHILE(@I <= @COUNT) DO
        INSERT INTO Tag_ClassifiedInfo(TagId,Category,Information)
        SELECT  TagIdIn,
				ExtractValue(classificationInfoAsXML,CONCAT('/classifications/classification[',@I,']/Category')),
				ExtractValue(classificationInfoAsXML,CONCAT('/classifications/classification[',@I,']/Information'));
        SET @I = @I + 1;
    END WHILE;
 END $$ 

DELIMITER $$
 CREATE PROCEDURE SP_GetTagClassification(
	IN TagIdIn BIGINT
)
BEGIN
	SELECT Category,Information FROM Tag_ClassifiedInfo where TagId=TagIdIn order by Category;
END $$ 


DELIMITER ;
