' Code from Microsoft's Visual Basic tutorial.

' Allow easy reference to the System namespace classes.
Imports sys = System.test

' This module houses the application's entry point.
Public Module modmain
   ' Main is the application's entry point.
   Sub Main()
     ' Write text to the console.
     Console.WriteLine ("Hello World using Visual Basic!")
   End Sub

    Sub tellOperator(ByVal task As String)
        Dim stamp As Date
        stamp = TimeOfDay()
        MsgBox("Starting " & task & " at " & CStr(stamp))
    End Sub
End Module

Function yesterday() As Date  
End Function  
  
Function findSqrt(ByVal radicand As Single) As Single  
End Function 

Function hypotenuse(ByVal side1 As Single, ByVal side2 As Single) As Single
	Return Math.Sqrt((side1 ^ 2) + (side2 ^ 2))
End Function


