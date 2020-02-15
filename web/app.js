var application = angular.module("PhysicsParticles", ["ngRoute", "ngSanitize"]);

application.config(function ($routeProvider) {
    $routeProvider
        .when("/", { templateUrl: "table.html", controller: "TableController" })
        .when("/particle/:particleName", { templateUrl: "particle.html", controller: "ParticleController" });
});

application.directive("mathematics", function () {
    return {
        restrict: "E",
        link: function (scope, element, attributes) {
            var contentType = attributes.contentType;
            var content = attributes.content;
            if (typeof (katex) === "undefined") {
                require(["katex"], function (katex) {
                    katex.render(content, element[0]);
                });
            }
            else {
                katex.render(content, element[0]);
            }
        }
    }
});

application.directive("compile", ["$compile", function ($compile) {
    return function (scope, element, attributes) {
        scope.$watch(function (scope) {
            return scope.$eval(attributes.compile);
        }, function (value) {
            element.html(value);
            $compile(element.contents())(scope);
        });
    };
}]);

class Database {
    constructor(data) {
        this._data = data;
        
            var charges = ["+1", "+2/3", "+1/3", "0", "-1/3", "-2/3", "-1"];
               var hues = [5, 15, 35, 110, 170, 195, 215];
        
        this._particlesObject = {}

        this._data.Particles.forEach(p => {
            p.U = {};

               
                   if (p.Mass != undefined ){
            
                  p.U.mass1 = p.Mass.filter(m => m.UnitClass == "kg" && m.Rounding == "3sf")[0].HTML;
                  p.U.mass2 = p.Mass.filter(m => m.UnitClass == "eV" && m.Rounding == "3sf")[0].HTML;
                  p.U.mass3 = p.Mass.filter(m => m.UnitClass == "u" && m.Rounding == "3sf")[0].HTML;}
                  
                        p.U.relativeCharge = p.RelativeCharge.replace("-", "&minus;");
                  p.U.charge = p.Charge.filter(c => c.UnitClass == "C" && c.Rounding == "3sf")[0].HTML;

                      






                        if (p.MeanLifetime != undefined && p.MeanLifetime != "stable"){                  
                  p.U.meanLifetime = p.MeanLifetime.filter(t => t.UnitClass == "s" && t.Rounding == "3sf")[0].HTML;}
                  
                     var i = charges.indexOf(p.RelativeCharge);

                       p.U.hue = hues[i]      ;
                           p.U.style = "background-color: hsl(" + p.U.hue + ", 100%, 95%); border-color: hsl(" + p.U.hue + ", 100%, 85%); color: hsl(" + p.U.hue + ", 70%, 40%);";
                       
                       this._particlesObject[p.Reference] = p;
        });
    }

    get particles() {
        return this._data.Particles;    }
        
               get  gridData (){
                   return this._particlesObject;
               }
        
        getParticleWithURLReference(urlReference) {
        var ps = this.particles.filter(p => p.URLReference == urlReference);

        return (ps.length > 0) ? ps[0] : null;
    }
}

application.factory("dataService", ["$http", function ($http) {
    var dataService = {
        data: null,
        getData: function () {
            var that = this;

            if (this.data != null) {
                return new Promise(function (resolve, reject) { return resolve(that.data); });
            }

            return $http.get("particles.json").then(function (response) {
                that.data = response.data;

                return response.data;
            });
        }
    };

    return dataService;
}]);

application.directive("particle", function () {
    return {
        restrict: "E",
        templateUrl: "particle-block.html",
        scope: {
            particle: "=data"
        }
    };
});

function getParticleSymbol(particle) {
    return (!particle) ? "" : "<mathematics content-type=\"latex\" content=\"" + particle.MainSymbol + "\"></mathematics>"
}

application.controller("TableController", ["$scope", "$routeParams", "dataService", "$rootScope", "$location", function TableController($scope, $routeParams, dataService, $rootScope, $location) {

    dataService.getData().then(function (data) {
        var database = new Database(data);

        $scope.particles = database.gridData;
    });

    $scope.getParticleSymbol = getParticleSymbol;

    $scope.goToParticlePage = function (particle) {
        $location.url("/particle/" + particle.URLReference);
    }
}]);

application.controller("ParticleController", ["$scope", "$routeParams", "dataService", "$rootScope", function ParticleController($scope, $routeParams, dataService, $rootScope) {

    dataService.getData().then(function (data) {
        var database = new Database(data);

        $scope.particle = database.getParticleWithURLReference($routeParams.particleName);
    });

    $scope.getParticleSymbol = getParticleSymbol;

}]);