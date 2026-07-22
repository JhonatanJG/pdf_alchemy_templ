from cmdline import Cmdline


from parseargs import PDFArgumentParser

def main():
    parser = PDFArgumentParser()
    args = parser.get_args()
    app = Cmdline(args)

    print("""
'||'''|, '||'''|. '||''''|                                 
 ||   ||  ||   ||  ||  .                                   
 ||...|'  ||   ||  ||''|                                   
 ||       ||   ||  ||                                      
.||      .||...|' .||.                                     
                                                           
                                                           
     /.      '||`       '||                               
    // \\      ||         ||                               
   //...\\     ||  .|'',  ||''|, .|''|, '||),,(|,  '||  ||`
  //     \\    ||  ||     ||  || ||..||  || || ||   `|..|| 
.//       \\. .||. `|..' .||  || `|...  .||    ||.      || 
    """)
    match app.args:
        case app.args.total_pages:
            app.get_num_pages()
        case app.args.split:
            app.split_pdf()
        case app.args.delete:
            app.del_range()
        case app.args.crop_half:
            app.crop_half()
        case app.args.command:
            if app.args.command == "add":
                app.add_pdf()
        case _:
            print("No arguments used, try 'uv run main.py -h'")


if __name__ == "__main__":
    main()
