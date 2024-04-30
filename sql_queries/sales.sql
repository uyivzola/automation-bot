SELECT D.Name        AS DocKind,
       i.Number      AS InvoiceNumber,
       C.Inn         AS Inn,
       C.FindName    AS ClientName,
       PCM.Name      AS ClientManager,
       G.GoodId      as GoodId,
       G.Name        AS Good,
       M.Name        AS Producer,
       il.Kolich     as Quantity,
       il.pSumma     AS TotalAmount,
       i.DataEntered as DataEntered
FROM INVOICELN il
         JOIN INVOICE i ON il.InvoiceId = i.InvoiceId
         JOIN PERSONAL PIM ON i.PersonalId = PIM.PersonalId
         JOIN DOCKIND D ON i.DocKindId = D.DocKindId
         JOIN CLIENT C ON i.ClientId = C.ClientId
         JOIN INCOMELN incl ON il.IncomeLnId = incl.IncomeLnId
         JOIN Good G ON incl.GoodId = G.GoodId
         JOIN Producer M ON M.ProducerId = G.ProducerId
         JOIN PERSONAL PCM ON C.PersonalId = PCM.PersonalId
         JOIN OFFICE O ON C.OfficeId = O.OfficeId
WHERE year(i.DataEntered) = 2024
  and month(i.DataEntered) = 4
  and i.Number = '69257'

ORDER BY i.DataEntered DESC
--12 341 517
-- 12341517

select i.Number      as InvoiceNumber,
       D.Name        as DocKind,
       C.Inn         as INN,
       C.FindName    as ClientName,
       PCM.Name      as ClientManager,
       i.pSumma      as TotalAmount,
       i.DataEntered as DataEntered
from INVOICE I
         join CLIENT C on I.ClientId = C.ClientId
         join PERSONAL PCM on C.PersonalId = PCM.PersonalId
         join DocKind D on I.DocKindId = D.DocKindId
where (D.Name in (N'Возврат товара от покупателя',
                  N'Оптовая реализация',
                  N'Финансовая скидка'))
  and i.pSumma > 4000000
  and CONVERT(date, i.DataEntered) = CONVERT(date, GETDATE()) -- today's data
order by i.DataEntered


select cast(getdate() as date)

select i.Number      as InvoiceNumber,
       D.Name        as DocKind,
       C.Inn         as INN,
       C.FindName    as ClientName,
       PCM.Name      as ClientManager,
       i.pSumma      as TotalAmount,
       i.DataEntered as DataEntered
from INVOICE I
         join CLIENT C on I.ClientId = C.ClientId
         join PERSONAL PCM on C.PersonalId = PCM.PersonalId
         join DocKind D on I.DocKindId = D.DocKindId
where (D.Name in (N'Возврат товара от покупателя',
                  N'Оптовая реализация',
                  N'Финансовая скидка'))
--   and i.pSumma > {amount}
  and CONVERT(date, i.DataEntered) = CONVERT(date, GETDATE()) -- today's data
order by i.DataEntered

-- CLIENT LIST
-- sergeli new => 16 591
-- ASkGlobal ==> 48 175

select distinct C.FindName as FindName,
                C.Inn      as INN,
                C.Address as Address,
                P.Name     as ClientManager
from Client C
         join Personal P on C.PersonalId = P.PersonalId
where P.name in ('(Опт) Нафасов Акмаль',
                 '(Опт) Юлдашева Мадина',
                 '(Опт) Саддинова Севинч',
                 '(Опт) Хабибуллаева Гулнозахон',
                 'Ёкубов Хикматилло'
    )
-- where C.inn in ('305621591'
--     )


select i.Number      as InvoiceNumber,
       D.Name        as DocKind,
       G.GoodId      as GoodId,
       G.Name        as GoodName,
       P.Name        as ProducerName,
       il.kolich     as Quantity,
       C.Inn         as INN,
       C.FindName    as ClientName,
       PCM.Name      as ClientManager,
       il.pSumma     as TotalAmount,
       i.DataEntered as DataEntered
from INVOICE I
         join CLIENT C on I.ClientId = C.ClientId
         join invoiceln il on il.InvoiceId = i.InvoiceId
         join PERSONAL PCM on C.PersonalId = PCM.PersonalId
         join IncomeLn incl on il.IncomeLnId = incl.IncomeLnId
         join Good G on incl.GoodId = G.GoodId
         join PRODUCER P on G.ProducerId = P.ProducerId
         join DocKind D on I.DocKindId = D.DocKindId
where (D.Name in (N'Оптовая реализация',
                  N'Финансовая скидка'))
  and i.pSumma > 1000000
  and CONVERT(date, i.DataEntered) = CONVERT(date, GETDATE()) -- today's data

order by i.DataEntered


select i.Number      as InvoiceNumber,
       D.Name        as DocKind,
       C.FindName    as ClientName,
       PCM.Name      as ClientManager,
       G.Name        as GoodName,
       P.Name        as ProducerName,
       il.kolich     as Quantity,
       il.pSumma     as ProductTotalAmount,
       i.DataEntered as DataEntered
from INVOICE I
         join CLIENT C on I.ClientId = C.ClientId
         join invoiceln il on il.InvoiceId = i.InvoiceId
         join PERSONAL PCM on C.PersonalId = PCM.PersonalId
         join IncomeLn incl on il.IncomeLnId = incl.IncomeLnId
         join Good G on incl.GoodId = G.GoodId
         join PRODUCER P on G.ProducerId = P.ProducerId
         join DocKind D on I.DocKindId = D.DocKindId
where (D.Name in (N'Оптовая реализация',
                  N'Финансовая скидка'))
  and i.pSumma > 1000000
  and CONVERT(date, i.DataEntered) = CONVERT(date, GETDATE()) -- today's data
order by i.DataEntered