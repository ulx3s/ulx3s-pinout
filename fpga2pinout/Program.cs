using System;
using System.IO;

namespace fpga2pinout
{
    class Program
    {
        /// <summary>
        /// ensure all new lines are using Environment.NewLine (typically Cr/Lf on Windows, Lf on Mac/Linux)
        /// </summary>
        /// <param name="forFile"></param>
        static string NormalizeLineEndings(string forString)
        {
            string CrLfNormalize = forString;
            CrLfNormalize = CrLfNormalize.Replace("\r\n", "\n");
            CrLfNormalize = CrLfNormalize.Replace("\n\r", "\n");
            CrLfNormalize = CrLfNormalize.Replace("\r", "\n");
            CrLfNormalize = CrLfNormalize.Replace("\n", Environment.NewLine);
            return CrLfNormalize; 
        }

        static void ProcessFile(string f)
        {
            string outputFile = f + "output.txt";
            Console.WriteLine("Processing file: {0} ...", f);

            string ConstraintText = File.ReadAllText(f);
            File.WriteAllText(outputFile, "");

            ConstraintText = NormalizeLineEndings(ConstraintText);

            string[] ConstraintLine = ConstraintText.Split(Environment.NewLine);

            for (int i = 0; i < ConstraintLine.Length; i++)
            {
                //   0      1    2       3    4  5   6      7
                // LOCATE COMP "gn[6]" SITE "C7" ;# J1_17- GN6
                //
                // 
                // [
                //    ("6", "gpio"),
                //    ("GP0", "gpsingle"),
                // ],
                string[] LineItems = ConstraintLine[i].Split(" ");
                if (LineItems[0].ToUpper() == "LOCATE" )
                {
                    string comp = LineItems[2].Replace("\"", "");
                    string site = LineItems[4].Replace("\"", "");

                    File.AppendAllText(outputFile, "["         + Environment.NewLine +
                                                   "    (\""   + comp  +"\", comp),"  + Environment.NewLine +
                                                   "    (\""   + site + "\", site),"  + Environment.NewLine +
                                                   "],"                               + Environment.NewLine

                        );

                }
            }
        }

        static void Main(string[] args)
        {
            string param = args[0];

            if (param != "")
            {
                ProcessFile(param);
            }
            

        }
    }
}
