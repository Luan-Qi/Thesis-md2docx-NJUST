Option Explicit

' Open a DOCX in Microsoft Word, update every field (so the table of contents
' gets real page numbers), and save it back as DOCX.
'
' USAGE: cscript //nologo word_update_fields.vbs input.docx [output.docx]
'
' This is the Word-side counterpart of `md2docx refresh-fields`. It is safe to
' run repeatedly: the result contains no dirty fields and references nothing
' outside the document, so Word opens it without prompting.

Dim objWord, doc, toc
Dim inputPath, outputPath

If WScript.Arguments.Count < 1 Then
    WScript.Echo "USAGE: cscript //nologo word_update_fields.vbs input.docx [output.docx]"
    WScript.Quit 64
End If

inputPath = WScript.Arguments.Item(0)
If WScript.Arguments.Count >= 2 Then
    outputPath = WScript.Arguments.Item(1)
Else
    outputPath = inputPath
End If

Set objWord = CreateObject("Word.Application")
objWord.Visible = False
objWord.DisplayAlerts = 0

On Error Resume Next
' Open read-write (third argument False) so the refreshed document can be saved.
Set doc = objWord.Documents.Open(inputPath, False, False, False, "", "", False, "", "", 0, 0, False, True, 0, True, "")

If (doc Is Nothing) Or (Err.Number <> 0) Then
    WScript.Echo "OPEN_ERROR:" & Err.Number & ":" & Err.Description
    objWord.Quit
    WScript.Quit 2
End If

Err.Clear
doc.Fields.Update
For Each toc In doc.TablesOfContents
    toc.Update
Next
doc.Repaginate
Err.Clear

doc.SaveAs2 outputPath, 16
If Err.Number <> 0 Then
    WScript.Echo "SAVE_ERROR:" & Err.Number & ":" & Err.Description
    doc.Close False
    objWord.Quit
    WScript.Quit 3
End If

doc.Close False
objWord.Quit
