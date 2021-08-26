import pandas as pd
from os import walk
import xlsxwriter
from xlsxwriter.workbook import Workbook
from xlsxwriter.worksheet import Worksheet
from django.conf import settings


def createOutputFile(df, brand_name):
    workbook = xlsxwriter.Workbook(
        f'{settings.BASE_DIR}/edi/static/edi/{brand_name}.xlsx')
    worksheet1 = workbook.add_worksheet()

    common_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'shrink': True,
        'border': True,
        'bold': True,
        'font_size': 11,
    })

    date_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'shrink': True,
        'border': True,
        'bold': True,
        'num_format': 'dd/mm/yy',
        'font_size': 11,
    })

    hidden_format = workbook.add_format({
        'hidden': True,
    })

    currency_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'shrink': True,
        'border': True,
        'bold': True,
        'num_format': '$#,##0.00',
        'font_size': 16,
    })

    def get_col_width(title, series):
        return max([len(str(i).strip()) for i in series] + [len(str(title).strip())])

    row = 0
    col = 0

    for label, content in df.iteritems():
        label = label.strip() if isinstance(label, str) else label
        cell_format = common_format
        worksheet1.write(row, col, label, cell_format)
        if ord('K') - ord('A') == col:
            cell_format = date_format  # bailment date format
        row += 1
        for index, value in content.items():
            if pd.isna(value):
                value = None
            value = value.strip() if isinstance(value, str) else value
            worksheet1.write(row, col, value, cell_format)
            row += 1

        # leave two rows for buttom sums
        for i in range(2):
            worksheet1.write(row, col, None, cell_format)
            row += 1

        # mimic auto width for each column
        width = get_col_width(label, content)
        worksheet1.set_column(col, col, width*1.25)
        row = 0
        col += 1

    # write sum for T V W column
    cols_sum = [chr(ord('T')+1), chr(ord('V')+1), chr(ord('W')+1)]
    nrows = len(df.index) + 1  # include header
    for c in cols_sum:
        worksheet1.write_formula(
            f'{c}{nrows + 2}', f'=SUM({c}2:{c}{nrows})', currency_format)
    cols_sum_name_col = ord('R')-ord('A')
    cols_sum_name_row = nrows+1
    # write 'total' before the sum(s)
    worksheet1.write(cols_sum_name_row, cols_sum_name_col,
                     'Total', currency_format)

    # 'approved' column width manually set to 40
    worksheet1.set_column('Z:Z', 40)
    for i in range(nrows+2):
        worksheet1.set_row(i, 30)

    # hide these coloumns
    columns_hidden = ['B', 'C', chr(ord('F')+1), chr(ord('G')+1), chr(
        ord('I')+1), chr(ord('R')+1), chr(ord('S')+1), chr(ord('U')+1), chr(ord('X')+1)]
    for c in columns_hidden:
        worksheet1.set_column(f'{c}:{c}', 0, hidden_format)

    workbook.close()


def process_edi_files():
    files = []
    for (dirpath, dirnames, filenames) in walk(f'{settings.MEDIA_ROOT}'):
        files.extend(filenames)
        break
    csvs = [f for f in files if f[-4:] == ".csv"]

    li = []
    for csv in csvs:
        df = pd.read_csv(f'./media/{csv}',
                         index_col=None, header=0, parse_dates=[9])
        li.append(df)

    if len(li) == 0:
        exit()

    # clean column names becuase there are leading and trailing spaces...
    column_names = [str(i).strip() for i in li[0].columns]
    df = pd.concat(li, axis=0, ignore_index=True)
    df.columns = column_names

    # parse dealer code data, so we can match dealer code to dealer name
    dealer_code_df = pd.read_excel(
        f'{settings.BASE_DIR}/edi/utils/Dealer Code - 2022.xlsx')
    dealer_info = dealer_code_df.iloc[7:, 1:11].reset_index(drop=True)
    dealer_codes = dealer_code_df.iloc[7:, 14].reset_index(drop=True)

    locations = []
    for (index, data) in dealer_info.iterrows():
        loc = next(filter(lambda x: not pd.isna(x), data), None)
        locations.append(loc)

    dealer_dict = {}
    for index, value in enumerate(dealer_codes):
        if not pd.isna(value):
            dealer_dict[str(value).strip()] = str(locations[index]).strip()

    # get dealer code column
    dc = df.iloc[:, 4]
    dealers = []
    for i in dc:
        dealers.append(dealer_dict.get(str(i).strip(), 'UNKNOWN'))

    # insert dealer name column into the correct column
    df.insert(5, "Dealer", dealers)

    # change HOLDEN to GMSV in the make column
    col_make_id = ord('N') - ord('A')
    for index, cell in enumerate(df.iloc[:, col_make_id]):
        if str(cell).upper() == 'HOLDEN':
            df.iat[index, col_make_id] = 'GMSV'

    # create outfile file by brand names
    for name, groupby in df.groupby('Supplier'):
        createOutputFile(groupby, name)

    # finally create a all-in-one file
    createOutputFile(df, 'Overall')
