using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PhysicsParticles.Compiler
{
    public class Particle
    {
        public string Reference { get; set; }
        public string Title { get; set; }
        public string Symbol { get; set; }
        public IList<string> Classes { get; set; }

    }
}
