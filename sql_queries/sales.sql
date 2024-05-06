SELECT O.Name        as Office,
       D.Name        AS DocKind,
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
  and month(i.DataEntered) = 2
  and (G.Name like '%форсил со%' or
       G.Name like '%риномакс х%')
  and il.Kolich >= 0
ORDER BY i.DataEntered DESC;


-- Sales
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
--   and i.pSumma > 4000000
  and year(i.DataEntered) >= 2020
--   and CONVERT(date, i.DataEntered) = CONVERT(date, GETDATE()) -- today's data
order by i.DataEntered


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


-- OTC PRODUCTS
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
  and year(i.DataEntered) >= 2024
  and G.GoodId in (
                   '72253',
                   '99374',
                   '78281',
                   '52482',
                   '52228',
                   '79498',
                   '101125',
                   '99178',
                   '127123',
                   '98453',
                   '66239',
                   '79218',
                   '78753',
                   '75461',
                   '56066',
                   '68177',
                   '70114',
                   '70069',
                   '70070',
                   '79423',
                   '82480',
                   '79027',
                   '75583',
                   '79500',
                   '97588',
                   '99287',
                   '101099',
                   '72678',
                   '72254',
                   '51312',
                   '55790',
                   '100504',
                   '76401',
                   '82668',
                   '88055',
                   '62315',
                   '78546'
    )
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
  and CONVERT(date, i.DataEntered) = CONVERT(date, GETDATE()) -- today's data
order by i.DataEntered


select C.ClientId, C.Findname, C.Inn, P.Name
from Client C
         join Personal P on C.PersonalId = P.PersonalId
-- where C.FindName like '%Ф-м%'

-- good ids with
select G.GoodId, G.Name
from GOod G

-- ZamonaRano Sales
select i.Number      as InvoiceNumber,
       D.Name        as DocKind,
       G.GoodId      as GoodId,
       G.Name        as GoodName,
       P.Name        as ProducerName,
       il.kolich     as Quantity,
       C.Inn         as INN,
       C.FindName    as ClientName,
       C.Phone       as PhoneNumber,
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
                  N'Финансовая скидка',
                  N'Возврат товара от покупателя'))
  and P.Name like '%Zamona Ra%'
  and month(i.DataEntered) = 4
  and year(i.DataEntered) = 2024

SELECT EOMONTH(GETDATE()) AS END_OF_MONTH;
DECLARE @DateBegin DATETIME;
DECLARE @DateEnd DATETIME;

-- Calculate the start of the current month
SET @DateBegin = DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0);

-- Set the end date as the current date
SET @DateEnd = GETDATE() + 1;

-- Call the stored procedure with the calculated dates
EXEC gTOandFSkidka @DateBegin, @DateEnd;


select distinct C.FindName, C.Inn, P.Name, sum(I.pSumma)
from CLIENT C
         join PERSONAL P on C.PersonalId = P.PersonalId
         join Invoice I on C.ClientId = I.ClientId
where i.DataEntered = 2024
group by P.Name, C.Inn, C.FindName
-- SALES_2024
SELECT DISTINCT C.FindName, C.Inn, P.Name, SUM(I.pSumma) as TOTAL_SALES_2024
FROM CLIENT C
         JOIN PERSONAL P ON C.PersonalId = P.PersonalId
         JOIN Invoice I ON C.ClientId = I.ClientId
WHERE YEAR(i.DataEntered) = 2024
  and month(I.DataEntered) between 1 and 4
GROUP BY C.FindName, C.Inn, P.Name, I.DataEntered;


-- SALES_2024
SELECT DISTINCT C.FindName    as ClientName,
                C.Inn         as INN,
                P.Name        as ClientManager,
                SUM(I.pSumma) as Total_sales_Jan_March
FROM CLIENT C
         JOIN
     PERSONAL P ON C.PersonalId = P.PersonalId
         JOIN
     Invoice I ON C.ClientId = I.ClientId
         join DocKind D on I.DocKindId = D.DocKindId

WHERE YEAR(I.DataEntered) = 2024
  AND MONTH(I.DataEntered) >= 1
  and MONTH(I.DataEntered) <= 3
  and (D.Name in (N'Возврат товара от покупателя',
                  N'Оптовая реализация',
                  N'Финансовая скидка'))
GROUP BY C.FindName, C.Inn, P.Name;



select O.Name        as Office,
       i.Number      as InvoiceNumber,
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
         JOIN OFFICE O ON C.OfficeId = O.OfficeId

where (D.Name in (N'Оптовая реализация',
                  N'Финансовая скидка',
                  N'Возврат товара от покупателя'))
  and month(i.DataEntered) = 4
  and year(i.DataEntered) = 2024


DECLARE @DateBegin DATETIME;
DECLARE @DateEnd DATETIME;

-- Calculate the start of the current month
SET @DateBegin = DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0);

-- Set the end date as the current date
SET @DateEnd = EOMONTH(GETDATE());

exec bGoodSaleByClientInforamtion_4 @DateBegin, @DateEnd

select O.Name         as Office,
       PCM.Name       as ClientManager,
       I.Number       as InvoiceNumber,
       I.Data         as Data,
--        AIR
       D.name         as DocKind,
       P.Name         as Producer,
       G.GoodId       as GoodId,
       G.Name         as GoodName,
       incl.SerialNo  as SerialNo,
       G.gkm_group    as gkm_group,
       S.Name         as Store,
       SD.Name        as StoreDep,
-- incl.OutPrice as OutPrice,
-- incl.OutKolich as OutKolich,
-- incl. as OutSumma,
       incl.BasePrice as BasePrice,
       C.FindName     as ClientName,
       C.Inn          as INN,
       C.Address      as ClientAddress,
       incl.Price     as Price,
       i.DownPayment  as DownPayment,
       i.PaymentTerm  as PaymentTerm,
       incl.ExpData   as ExpData,
-- Ct.Name as ClientType,
-- CtnNumber,
       R.name         as Region,
       i.DataEntered  as DataEntered
from Invoice as I
         join invoiceln as il on I.InvoiceId = il.InvoiceId
         join IncomeLn incl on il.IncomeLnId = incl.IncomeLnId
         left join Client C on I.ClientId = C.ClientId
         left join PERSONAL PCM on C.PersonalId = PCM.PersonalId
         left join GOOD G on incl.GoodId = G.GoodId
         left join CITY R on C.CityId = R.CityId
         left join Store S on I.StoreId = S.StoreId
         left join StoreDep SD on I.StoreDepId = SD.StoreDepId
         left join Producer P on G.ProducerId=P.ProducerId
         left join DocKind D on I.DocKindId = D.DocKindId
         left JOIN OFFICE O ON C.OfficeId = O.OfficeId
where year(i.DataEntered) >='2024' and month(i.DataEntered) = 5


