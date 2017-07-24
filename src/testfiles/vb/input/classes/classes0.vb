Class bankAccount
    Shared interestRate As Decimal
    Private accountNumber As String
    Private accountBalance As Decimal
    Public holdOnAccount As Boolean = False

    Public ReadOnly Property balance() As Decimal
        Get
            Return accountBalance
        End Get
    End Property

    Public Sub postInterest()
        accountBalance = accountBalance * (1 + interestRate)
    End Sub

    Public Sub postDeposit(ByVal amountIn As Decimal)
        accountBalance = accountBalance + amountIn
    End Sub

    Public Sub postWithdrawal(ByVal amountOut As Decimal)
        accountBalance = accountBalance - amountOut
    End Sub
End Class

Public Interface ICustomerInfo
    Event updateComplete()
    Property customerName() As String
    Sub updateCustomerStatus()
End Interface

Public Class customerInfo
    Implements ICustomerInfo
    ' Storage for the property value.
    Private customerNameValue As String
    Public Event updateComplete() Implements ICustomerInfo.updateComplete
    Public Property CustomerName() As String _
        Implements ICustomerInfo.customerName
        Get
            Return customerNameValue
        End Get
        Set(ByVal value As String)
            ' The value parameter is passed to the Set procedure
            ' when the contents of this property are modified.
            customerNameValue = value
        End Set
    End Property

    Public Sub updateCustomerStatus() _
        Implements ICustomerInfo.updateCustomerStatus
        ' Add code here to update the status of this account.
        ' Raise an event to indicate that this procedure is done.
        RaiseEvent updateComplete()
    End Sub
End Class

Public Class dictionary(Of entryType, keyType As {IComparable, IFormattable, New})
    Public Sub add(ByVal et As entryType, ByVal kt As keyType)
        Dim dk As keyType
        If kt.CompareTo(dk) = 0 Then
        End If
    End Sub
End Class

