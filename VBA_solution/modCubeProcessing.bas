Attribute VB_Name = "modCubeProcessing"
Option Explicit

' === Split data by concrete type (strict 45, 60, 45WP, 60WP) ===
Sub SplitByConcreteTypeStrict()
    Dim wsSrc As Worksheet: Set wsSrc = ThisWorkbook.Sheets("Raw")
    Dim lastRow As Long: lastRow = wsSrc.Cells(wsSrc.Rows.Count, "A").End(xlUp).Row

    Dim i As Long, mark As String, targetType As String
    Dim allowedTypes As Variant: allowedTypes = Array("45D", "60D", "45DWP", "60DWP")
    Dim dict As Object: Set dict = CreateObject("Scripting.Dictionary")

    ' Create or get 4 target sheets
    Dim t As Variant
    For Each t In allowedTypes
        Set dict(CStr(t)) = CreateOrClearSheet(CStr(t))
        wsSrc.Rows(1).Copy Destination:=dict(CStr(t)).Rows(1)
    Next t

    ' Loop through rows and sort into sheets
    For i = 2 To lastRow
        mark = wsSrc.Cells(i, "A").Value
        targetType = GetStrictConcreteType(mark)
        If dict.exists(targetType) Then
            Dim tgtWs As Worksheet: Set tgtWs = dict(targetType)
            Dim nextRow As Long: nextRow = tgtWs.Cells(tgtWs.Rows.Count, "A").End(xlUp).Row + 1
            wsSrc.Rows(i).Copy Destination:=tgtWs.Rows(nextRow)
        End If
    Next i
End Sub

' === Identify type: 45, 60, 45WP, 60WP ===
Function GetStrictConcreteType(mark As String) As String
    Dim is45 As Boolean, is60 As Boolean, isWP As Boolean

    is45 = (InStr(1, mark, "45D", vbTextCompare) > 0)
    is60 = (InStr(1, mark, "60D", vbTextCompare) > 0)
    isWP = (InStr(1, mark, "WP", vbTextCompare) > 0)

    If is45 And isWP Then
        GetStrictConcreteType = "45DWP"
    ElseIf is60 And isWP Then
        GetStrictConcreteType = "60DWP"
    ElseIf is45 Then
        GetStrictConcreteType = "45D"
    ElseIf is60 Then
        GetStrictConcreteType = "60D"
    Else
        GetStrictConcreteType = "Unknown"
    End If
End Function

Function CreateOrClearSheet(name As String) As Worksheet
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = ThisWorkbook.Sheets(name)
    On Error GoTo 0
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Sheets.Add(After:=Sheets(Sheets.Count))
        ws.name = name
    Else
        ws.Cells.Clear
    End If
    Set CreateOrClearSheet = ws
End Function

' === Merge same values in Pour Location (O) ===
Sub MergePourLocations(ws As Worksheet)
    Dim lastRow As Long, i As Long, startRow As Long, currentValue As String
    Dim col As String: col = "G"

    lastRow = ws.Cells(ws.Rows.Count, col).End(xlUp).Row
    i = 2

    Application.DisplayAlerts = False

    Do While i <= lastRow
        startRow = i
        currentValue = ws.Cells(i, col).Value

        Do While i <= lastRow And ws.Cells(i, col).Value = currentValue
            i = i + 1
        Loop

        If i - startRow > 1 Then
            With ws.Range(ws.Cells(startRow, col), ws.Cells(i - 1, col))
                .Merge
                .VerticalAlignment = xlCenter
            End With
        End If
    Loop

    Application.DisplayAlerts = True
End Sub

' === Merge every two rows in specified column (e.g., Cube Mark Prefix or Cube Number) ===
Sub MergeByTwoRowsInCol(ws As Worksheet, colLetter As String)
    Dim lastRow As Long, i As Long
    lastRow = ws.Cells(ws.Rows.Count, colLetter).End(xlUp).Row

    Application.DisplayAlerts = False

    For i = 2 To lastRow Step 2
        If i + 1 <= lastRow Then
            With ws.Range(ws.Cells(i, colLetter), ws.Cells(i + 1, colLetter))
                .Merge
                .VerticalAlignment = xlCenter
            End With
        End If
    Next i

    Application.DisplayAlerts = True
End Sub

' === Main controller: run all steps ===
Sub RunAllProcessingSteps()
    Call SplitByConcreteTypeStrict

    Dim ws As Worksheet
    For Each ws In ThisWorkbook.Sheets
        If ws.name = "45D" Or ws.name = "60D" Or ws.name = "45DWP" Or ws.name = "60DWP" Then
            Call MergePourLocations(ws)
            Call MergeByTwoRowsInCol(ws, "A")
            Call MergeByTwoRowsInCol(ws, "B")
        End If
    Next ws
End Sub
