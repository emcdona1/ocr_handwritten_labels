
 select TagId into @tagId from Tag_Word limit 1;
 CALL SP_AddTag('testRef2','tagNametest','imagePath','imageBlob',
 '<words>
	<word>
		<description>TestWord</description>
        <replacement>replaceMe</replacement>
        <vertices>[x0,y0,x1,y1,x2,y2,x3,y3]</vertices>
        <suggestions>[suggestion0,suggestion1, suggestion2, suggestion3, suggestion4]</suggestions>
        <category>ScienteficName</category>
	</word>
    <word>
		<description>TestWord</description>
        <replacement>replaceMe</replacement>
        <vertices>[x0,y0,x1,y1,x2,y2,x3,y3]</vertices>
        <suggestions>[suggestion0,suggestion1, suggestion2, suggestion3, suggestion4]</suggestions>
        <category>ScienteficName</category>
	</word>
 </words>'
 );
 
 CALL SP_UpdateTag(@tagid,
 '<words>
	<word>
		<description>UpdatedWord</description>
        <replacement>replacedVal</replacement>
        <vertices>[x0,y0,x1,y1,x2,y2,x3,y3]</vertices>
        <suggestions>[suggestion0,suggestion1, suggestion2, suggestion3, suggestion4]</suggestions>
        <category>UpdatedCategory</category>
	</word>
    <word>
		<description>TestWord2</description>
        <replacement>replaceMe2</replacement>
        <vertices>[x0,y0,x1,y1,x2,y2,x3,y3]</vertices>
        <suggestions>[suggestion0,suggestion1, suggestion2, suggestion3, suggestion4]</suggestions>
        <category>ScienteficName</category>
	</word>
 </words>'
 );
 
 CALL SP_DeleteTag(3);
 

 select * from Tag_info;
 select * from Tag_Image;
 select * from Tag_Word;
 
CALL SP_GetTagList('');

CALL SP_GetTagDetail(1);
 
 
 