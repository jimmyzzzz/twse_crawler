# 台灣證交所爬蟲

在當今python爬蟲大爆炸的時代，大家都想寫幾個爬蟲並在家裡架一個小型的資料庫來玩玩。
從爬蟲爬取證交所股價資料開始，到解析爬取的資料，最後再保存到資料庫中。在這篇repository中，便是實現了這樣的事情。

當你運行*daily_work.py*文件時，該程式便可以幫助你每日完成爬取到保存的一系列工作，也能自動幫助你判斷當天是否沒有開盤，需不需要爬取等工作。但是先別急，在開始運行該程式時，請先正確的配置相關的環境，然後讓電腦每天自動幫助你運行*daily_work.py*文件就可以了。

本篇會先介紹如何配置環境，使得整套系統可以正確運作，然後會介紹如何修改一些配置，使得整套系統可以按需要運作。

***

## 配置環境

下面將會介紹如何正確的配置相關環境，並讓電腦每日自動運行*daily_work.py*腳本。

但在開始之前請先確保你已經建立了一個可以使用的MySQL服務器，如果不知道如何架設可以參考我之前的這篇:
[在ubuntu/kubuntu中安裝MySQL Server](https://github.com/jimmyzzzz/Install_MySQL_Server_on_the_kubuntu)

並且已經安裝了下面的相關套件:
* `numpy`
* `pandas`
* `pymysql`

最後，建議先去閱讀這兩篇介紹[crawler_tool](https://github.com/jimmyzzzz/twse_crawler/blob/dev/How_to_crawl_data_using_crawler_tool.ipynb)和[mysql_tool](https://github.com/jimmyzzzz/twse_crawler/blob/dev/How_to_save_data_using_mysql_tool.ipynb)兩個套件用法的說明，可以有助於理解接下來的內容。這兩個套件的原始文件在 *./crawler_tool* 和 *./mysql_tool* 。

***

### 建立資料庫與資料表

首先你需要建立資料庫與資料表，你可以使用本文預設的名稱也可以使用自己設定的名稱，只不過如果是使用自己設定的名稱就需要之後必須修改或添加一些代碼來使得程式能運作正常。下面是預設的配置:
* 資料庫名稱: stock_db
* 資料表名稱: twse_stock
* 用戶名稱: testuser
* 用戶密碼: 123

下面是建立資料表的mysql指令，除了資料表名稱外都不建議修改:
```
CREATE TABLE `twse_stock` (       # 資料表名稱
`ID` INT NOT NULL AUTO_INCREMENT, # 資料編號
`date` DATE NULL,                 # 交易日
`stock_id` VARCHAR(32) NULL,      # 股票編號
`open` DECIMAL(9,3) NULL,         # 開盤價
`high` DECIMAL(9,3) NULL,         # 最高價
`low` DECIMAL(9,3) NULL,          # 最低價
`close` DECIMAL(9,3) NULL,        # 收盤價
`mean` DECIMAL(9,3) NULL,         # 平均價
`volume` INT NULL,                # 成交量
`record` INT NULL,                # 成交筆數
PRIMARY KEY (`ID`));
```

表格的各個欄位對應了爬蟲爬取到的各個欄位，如果需要查看爬蟲到底爬到了什麼資料可以在當前目錄下運行:
```
from crawler_tool import get_day_price
day_df = get_day_price(
    stock_id='1101',        # 股票名稱
    year=2022,              # 年份
    month=4,                # 月份
    day=1                   # 日期
)
print(day_df)
```
該代碼會顯示爬蟲爬取1101(台泥)在2022/4/1的日資料。

如果你使用預設的配置建立資料庫與資料表，則可以跳過建立連線工具和使用新建的連線工具的部份。直接跳到每日自動運行daily_work.py的部份。

***

### 建立連線工具

當爬蟲抓到資料後預設會使用`mysql_tool.twse_stock_portal`來建立連接並將資料保存到資料庫中。如果在上面建立資料庫時，使用的不是預設的資料庫名稱或是資料表名稱，那麼你會需要建立自己的一個連接工具。如果想要詳細了解這方面的使用方法可以查閱[How_to_save_data_using_mysql_tool.ipynb](https://github.com/jimmyzzzz/twse_crawler/blob/dev/How_to_save_data_using_mysql_tool.ipynb)。而如果只是需要一個簡單的模板，可以將下面的程式碼加入到*mysql_tool/mysql_portal.py*中:
```
class my_tab_portal(sqlif):
    def __init__(self, user, password):
        bd_name=你的資料庫名稱
        tab_name=你的資料表名稱
        conn=pymysql.connect(
            host=你的資料庫的HOST,
            port=你的資料庫的port,
            user=user,
            password=password,
            db=bd_name
        )
        
        super().__init__(conn=conn, tab=tab_name)
```
其中`bd_name`,`tab_name`,`host`,`port`是必填的項。

最後在`mysql_tool/__init__.py`中加入下面的代碼以方便調用`my_tab_portal`:
```
from mysql_tool.mysql_portal import my_tab_portal
```

***

### 使用新建的連線工具

當建立好新的連線工具後就可以調用新的連線工具了，打開*daily_work.py*找到`daily_df_to_twse_tab`函數，可以看到這兩行代碼:
```
twse_tab=twse_stock_portal(user='testuser', password='123')
twse_tab.insert_df(df)
```
第一行的意思是使用連線工具建立連接，第二行是使用連線工具插入抓取到的資料，你可以修改成:
```
my_tab=my_tab_portal(user=用戶帳號, password=用戶密碼)
my_tab.insert_df(df)
```
不要忘了在前面`from mysql_tool import my_tab_portal`。

***

### 每日自動運行daily_work.py

我們一樣使用corn

輸入指令編輯`crontab`:

        $ crontab -e

加入每天自動執行的腳本的設定:

        # 每天下午 6 點 30 分執行自動備份的腳本
        30 18 * * * python YOUR_PATH/daily_work.py >> file

該腳本會在每天下午6點30分自動執行腳本，並將執行狀況的資訊保存到`file`文件中。而如果資料有抓取成功，在將資料保存到資料庫前，會先保存一份資料到`daily_df.csv`檔案中，以防資料庫連接失敗。

如果是使用虛擬環境，比如anaconda。則需要使用該環境的python來執行*daily_work.py*腳本。以anaconda為例，在終端中輸入:`$ which python`，可以看到類似的路徑:`/home/MY_NAME/anaconda3/envs/MY_ENV/bin/python`，然後將該路徑取代掉自動執行的腳本中的`python`即可。

如果程式運行正常，應該會看到`file`文件中添加了類似的內容:
```
[2022-04-22] daily_crawler success: 52/52
crawler time cost: 1.22..., db time cost: 0.0...
```

***

## 修改配置

當系統已經可以正確運作之後，就可以通過修改其中的配置來使系統可以滿足需要了。
下面將著重在下面幾點:
1. 修改爬蟲爬取次數和間隔設定
2. 修改錯誤保存路徑
3. 修改股票名單備份路徑
4. 修改爬取的股票名單
5. 修改爬蟲函數

***

### 修改爬蟲爬取次數和間隔設定

*daily_work.py*中有使用到的爬蟲的函數如下:
* today_is_trading_days
* get_stock_list
* daily_crawler

只需要修改其中的`@try_loop_decorator(times=5, sleep_time=3)`就可以了，比較需要注意的是`daily_crawler`中並沒有裝飾器可以供修改，如果要修改則需要打開`crawler_tool/twse_stock_day_crawler.py`文件。

打開文件後可以通過修改全域變數`TIMES`和`SLEEP_TIME`來達到效果。但通常而言，爬取次數和間隔的設定不太需要修改。

***

### 修改錯誤保存路徑

當爬蟲或系統發生錯誤時，系統並不會回傳一個錯誤訊息並停止運作，而是會紀錄錯誤訊息並繼續運作。如果需要修改保存錯誤訊息的檔案路徑，可以找到該函數使用的`record_error_decorator`裝飾器，並修改其中的保存路即可。

而使用了`record_error_decorator`裝飾器的函數集中在*daily_work.py*和*crawler_tool/twse_stock_day_crawler.py*中。

***

### 修改股票名單備份路徑

當抓取股票股價資料前會先抓取股票名單，再根據股票名單抓取各個股票的股價資料。這使得爬蟲之間存在著依賴關係，一旦股票名單抓取失敗，則後面的所有爬蟲也將無法運作。於是就有了備份的需要，股票名單抓取成功後，會將抓取的結果備份起來，以防下次抓取發生了失敗。

所有需要備份功能的爬蟲函數都有`backup_decorator`裝飾器，只需要修改該裝飾器的參數便可以修改備份路徑。股票名單的抓取函數在*daily_work.py*中的`get_stock_list`函數中。

***

### 修改爬取的股票名單

預設爬取的是0050的成份股，如果要修改爬取的股票名單，可以修改*daily_work.py*中的`get_stock_list`函數。在`get_stock_list`函數中可以看到這麼一段:
```
return get_0050_list()
```
只需要修改這段的內容便可以改變爬取的股票名單了，下面是其他可以替代的函數:
* get_stock_id_list: 取得上市股票名單
* get_etf_id_list: 取得etf名單
* get_otc_id_list: 取得上櫃股票名單

也可以將多種名單合起來使用。

***

### 修改爬蟲函數

一但網站發生了修改或是網站搬家，原有的爬蟲將會無法正常運作。這時就需要新的爬蟲函數來取代舊的爬蟲函數。這時後需要修改*daily_work.py*中的`daily_crawler`函數，在該函數中可以看到其使用了`get_day_price`函數來抓取股價資料，這時候只需要將新的函數替換`get_day_price`函數即可。

**`建議:`** 可以將新函數的程式碼檔案放到`crawler_tool/`下，如同twse_stock_day_crawler.py檔案一樣，這樣分類方便管理。

***

## 後記

說實話，我一直在思考要不要讓修改配置的部份不要如此繁瑣，能不能通過類似修改配置文件的方式來達到目的，而不是通過修改程式碼的方式。但後來轉念一想，其實爬蟲本身就是一種需要常常修改程式碼的系統，許多情況的發生都可能會使得程式碼需要修改，建立一個動態的系統可能不是那麼現實，使用者本身就不可避免要觸碰到程式的部份。

那麼最好的方式就是以一種提供工具的方式來組織整個系統，不求設計一個能處理所有狀況的爬蟲，但可以設計一個可以快速設計出處理新狀況的爬蟲的工具。這也就是`crawler_tool`和`mysql_tool`包的由來。

`crawler_tool`包中的`crawlers.py`提供一些「初級」爬蟲而`crawler_decorator.py`提供爬蟲需要的裝飾器。你可以用這兩個模組建立複雜的爬蟲，`twse_stock_day_crawler.py`就是一個例子。

`mysql_tool`包中則是提供了操作mysql資料庫的界面，使用者不需要懂得mysql的語法也不需要為了組織mysql的指令在程式碼中拼接字串。只需要使用最自然的方式操作即可，這便是`mysql_interface`存在的目的。而具體連接到資料庫中的某個資料表，只需要通過繼承`mysql_interface`的方式建立一個界面即可，`mysql_portal.py`中的每個類都是例子。

最後感謝看到這邊的各位，希望這篇對你有所幫助。

***