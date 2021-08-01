using Svg;
using System;
using System.IO;

namespace svg2png
{
    // see https://github.com/svg-net/SVG

    class Program
    {
        static void ProcessFile(string fileName)
        {
            var outputFile = Path.GetDirectoryName(fileName) + @"\" + Path.GetFileNameWithoutExtension(fileName) + ".png";
            var thisSVG = SvgDocument.Open(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, fileName));
            thisSVG.Draw().Save(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, outputFile));
        }


        static void Main(string[] args)
        {
            if (args.Length == 0) 
            {
                Console.WriteLine("No file specified.");
                return;
            }

            string param = args[0];


            if (param != "")
            {
                ProcessFile(param);
            }

        }
    }
}
 
