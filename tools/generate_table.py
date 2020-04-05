import dash_html_components as html
from config import APP_COLORS, POS_NEG_NEUT


def generate_table(df, max_rows=10, is_master=False):
    # print(df.values.tolist()[-1])
    return html.Table(className="responsive-table",
                      children=[
                          html.Thead(
                              html.Tr(
                                  children=[
                                      html.Th(col.title()) for col in df.columns.values],
                                  style={'color': APP_COLORS['text']}
                              )
                          ),
                          html.Tbody(
                              [

                                  html.Tr(
                                      children=[
                                          html.Td(data) for data in d
                                      ], style={'color': APP_COLORS['text'],
                                                'background-color':quick_color(d[-1]),
                                                "border":"2px black solid"}
                                  )
                                  for d in df.values.tolist()] if not is_master else [

                                  html.Tr(
                                      children=[
                                          html.Td(data) for data in d
                                      ], style={'color': APP_COLORS['text'],
                                                "border":"2px black solid"}
                                  )
                                  for d in df.values.tolist()])
                      ],
                      style={"border":"2px black solid"}
                      )


def quick_color(s):
    # except return bg as app_colors['background']
    if s >= POS_NEG_NEUT:
        # positive
        return "#98FB98"
    elif s <= -POS_NEG_NEUT:
        # negative:
        return "#FF6347"
    else:
        return APP_COLORS['someothercolor']