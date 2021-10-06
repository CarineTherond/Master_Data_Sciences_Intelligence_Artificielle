##############################################################################################################################################
#Import handling
##############################################################################################################################################
from myTools import m_SQLconnector as m_sql

#The following modules are supposed not to be installed
from myTools import m_ModuleInstaller as mi
try:
    import pandas as pd
except:
    mi.installModule("pandas")
    import pandas as pd
    
    
##############################################################################################################################################
#SQL query frames 
##############################################################################################################################################
strQueryTemplateForAnswerColumn = """
			COALESCE(
				(
					SELECT a.Answer_Value
					FROM Answer as a
					WHERE
						a.UserId = u.UserId
						AND a.SurveyId = <SURVEY_ID>
						AND a.QuestionId = <QUESTION_ID>
				), -1) AS ANS_Q<QUESTION_ID> """

strQueryTemplateForNullColumnn = """ NULL AS ANS_Q<QUESTION_ID> """

strQueryTemplateOuterUnionQuery = """
    			SELECT
    					UserId
    					, <SURVEY_ID> as SurveyId
    					, <DYNAMIC_QUESTION_ANSWERS>
    			FROM
    				[User] as u
    			WHERE EXISTS
    			(
    					SELECT *
    					FROM Answer as a
    					WHERE u.UserId = a.UserId
    					AND a.SurveyId = <SURVEY_ID>
			    ) 
                """

#Request required by the cursor of first for loop    
currentSurveyId_request = """
                    SELECT SurveyId 
                    FROM Survey
                    ORDER BY SurveyId
                    """

#Request required by the cursor of second for loop                    
currentQuestionCursor_request = """
            SELECT *
            FROM
            (
				SELECT																
					SurveyId,
					QuestionId,
					1 as InSurvey
				FROM
					SurveyStructure
				WHERE
					SurveyId = @currentSurveyId

				UNION

				SELECT								  
					@currentSurveyId as SurveyId,
					Q.QuestionId,
					0 as InSurvey
				FROM
					Question as Q
				WHERE NOT EXISTS					  
				(
					SELECT *
					FROM SurveyStructure as S
					WHERE S.SurveyId = @currentSurveyId 
                        AND S.QuestionId = Q.QuestionId  
				) 
            ) AS t
            ORDER BY QuestionId
            """
            
#Request needed to save SurveyStructure Table
SurveyStructureRequest = """
                    SELECT * 
                    FROM SurveyStructure
                    """            
                        
                    
##############################################################################################################################################
#Dynamic query construction from Survey_Sample_A19 DataBase
##############################################################################################################################################
def fn_GetAllSurveyDataSQL(MySQLconnector: m_sql.SQLconnector, fileSurvey: str) -> str:
    """ Pivot of Answer SQL table such that each rows deliver the following information :
            UserID, SurveyId, ANS_Q1, ..., ANS_Qn
    """

    strCurrentUnionQueryBlock = ""
    strFinalQuery = ""

    try:
        #Current SQL SurveyStructure Table saving
        #########################################
        SurveyStructureTable = MySQLconnector.ExecuteQuery_withRS(SurveyStructureRequest)
        SurveyStructureTable.fillna('NULL').to_csv(fileSurvey) 

        #Dynamic query construction
        ###########################
        surveyCursor = MySQLconnector.ExecuteQuery_withRS(currentSurveyId_request)["SurveyId"]
        nb_survey = len(surveyCursor)
        
        #FOR EACH SURVEY, IN currentSurveyId, WE NEED TO CONSTRUCT THE ANSWER COLUMN QUERIES
        for currentSurveyId in range(nb_survey):
                    
            #I want a resultset of SurveyId, QuestionId, flag InSurvey indicating whether question is in the survey structure
            tt = MySQLconnector.ExecuteQuery_withRS(currentQuestionCursor_request.replace("@currentSurveyId", str(surveyCursor[currentSurveyId])))
    
            currentSurveyIdInQuestion = tt["SurveyId"]
            currentQuestionID = tt["QuestionId"]
            currentInSurvey = tt["InSurvey"]
            strColumnsQueryPart = ""
    
            nb_question = tt.shape[0]
            for currentQuestionCursor in range(nb_question):
    
                #CURRENT QUESTION IS NOT IN THE CURRENT SURVEY: THEN BLOCK SPECIFICATION: THE VALUES IN THIS COLUMN WILL BE NULL
                if (currentInSurvey[currentQuestionCursor] == 0) :
                    
                    strColumnsQueryPart = strColumnsQueryPart \
                        + strQueryTemplateForNullColumnn.replace('<QUESTION_ID>', str(currentQuestionID[currentQuestionCursor]))
        
                else :
    
                    strColumnsQueryPart = strColumnsQueryPart \
                        + strQueryTemplateForAnswerColumn.replace('<QUESTION_ID>', str(currentQuestionID[currentQuestionCursor]))
                    
                #Place a comma between column statements, except for the last one
                if (currentQuestionCursor != (nb_question - 1)):
                    strColumnsQueryPart = strColumnsQueryPart + ' , '
    
    
            strCurrentUnionQueryBlock = strQueryTemplateOuterUnionQuery.replace('<DYNAMIC_QUESTION_ANSWERS>', strColumnsQueryPart)
            strCurrentUnionQueryBlock = strCurrentUnionQueryBlock.replace('<SURVEY_ID>', str(surveyCursor[currentSurveyId]))
            strFinalQuery = strFinalQuery + strCurrentUnionQueryBlock
    
            if(currentSurveyId != (nb_survey - 1)):
                strFinalQuery = strFinalQuery + " UNION "

        return strFinalQuery
    
    except Exception as exc:
        MySQLconnector.Close()
        print("\nException : ", exc)
        raise 


