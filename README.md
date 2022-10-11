# data-center

## usage
本项目采用flask，主要用到了os，re，pandas，requests，typing等库。
python版本建议3.6及以上，直接运行下面的命令即可执行后端
- pip install -r requirements.txt
- python main.py
注：
1. requirements.txt中的包可能不全，我因为没用venv，freeze出来手动筛了一遍，有什么缺失的库用pip install安装即可。
2. 文件路径只有部分使用了os.path.join。

## 设计思路
### 文件（夹）介绍
接下来我对几个重要文件及文件夹进行简单介绍。
- oerv_obsdata 文件夹克隆自[OBS构建数据仓库](https://gitee.com/phoebe-xi/oerv_obsdata)，本项目目前几乎所有数据都是取自此处。
- oerv_script 内主要要两个文件夹，分别是oerv_obsdata和script文件夹，其中oerv_obsdata文件夹同上，但是用途有所区别。因为本项目有一个一键更新数据仓库的功能，所以在将该oerv_obsdata克隆到本地后，执行数据更新代码，再将其推送到gitee，总而言之，其是作为一个中间文件夹存在的；script克隆自[OBS数据抓取仓库](https://gitee.com/phoebe-xi/oerv_script/tree/master)，修改了部分代码，详情可见oerv_script的README。
- changelog.md 文件主要记录版本变动，包括一些需求和代码设计的描述。
- main.py是flask的入口文件，在执行后端的时候执行“python main.py”。
- ObservatoryPackages.py文件存放网页端Package Observatory分区相关的api。
- ObservatoryProjects.py文件存放网页端Project Observatory分区相关的api。
- Update.py文件主要用于更新数据，包括1. 只从远程拉取文件到oerv_obsdata；2. 更新远程的oerv_obsdata仓库并拉取数据到本地。其中第二项功能可能需要几分钟时间。
- Utils.py中包含提取文件差异的代码。可以通过commit id, path等参数对所需要比较的文件进行配置。

### 如何新增一个页面对应的api
参考ObservatoryPackages.py等文件创建一个新文件，并在main.py中注册蓝图即可。
