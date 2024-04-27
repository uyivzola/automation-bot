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


select cast(getdate() as  date)